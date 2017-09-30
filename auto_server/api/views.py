from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from repository.models import Disk, Server, Memory, NIC
from api.src.plugin import PluginManager


@csrf_exempt
def server(request):
    # 客户端请求头指定是json字符串，request.post无法获取内容，需要用request.body, 然后反序列化
    data = json.loads(request.body.decode('utf-8'))
    # print('data---------%r'%data)

    # 每次发过来的数据，是一台server的，根据server标识从数据库中取出server_obj; 然后再对与该server相关的硬件进行入库/修改
    if not data['basic']['status']:
        print('错误信息')
        return HttpResponse('something wrong')

    hostname = data['basic']['detail']['hostname']
    server_obj = Server.objects.filter(hostname=hostname).first()

    if server_obj: # 取出其相关的硬件信息
        # 改写为插拔式，执行任何操作，都需要两个参数：server_obj ,data
        # 先配置，再利用反射，执行。。。
        # server信息，客户端一定会传过来，而且也必须处理，因此不能设计为可插拔，在上面单独处理/或在Plugin_manager中单独处理
        plugin_manager = PluginManager(server_obj, data)
        plugin_manager.execute()

    else: # #####################################################################################新增服务器和硬件
        """ 
       'basic': {'status': True, 
                 'detail': {'os_platform': 'linux', 'os_version': 'CentOS release 6.6 (Final)\nKernel \r on an \\m',  'hostname': 'c1.com'},
                 'error_msg': None}
        """
        ################################## 新增服务器
        server_dict = data['basic']['detail']
        os_platform = server_dict['os_platform']
        os_version = server_dict['os_version']

        new_server = Server(hostname=hostname,
                            os_platform=os_platform,
                            os_version=os_version)
        new_server.save()

        ################################# 新增硬盘
        if not data['disk']['status']:
            return HttpResponse('something wrong')  # 记录错误日志

        disk_dict = data['disk']['detail']
        # {'0': {'slot': '0', 'model': 'xxx', }, '1': {'slot': '0', 'model': 'xxx', }}
        disk_list = []
        for slot, disk in disk_dict.items():
            disk_obj = Disk(**disk)  # 批量接收字典参数用**, 批量接收列表用*
            disk_obj.server_obj = new_server
            disk_list.append(disk_obj)

        Disk.objects.bulk_create(disk_list)
        print('添加硬盘信息完成')

        ################################ 新增内存
        """
       'memory': {'status': True,
                  'detail': {'DIMM #0': {'capacity': 1024,  'slot': 'DIMM #0',  'model': 'DRAM',  'speed': '667 MHz', 'manufacturer': 'Not Specified','sn': 'Not Specified'},
                            ... 
       """
        if not data['memory']['status']:
            return HttpResponse('something wrong')

        memory_dict = data['memory']['detail']
        memory_list = []
        for slot, memory in memory_dict.items():
            memory_obj = Memory(**memory)
            memory_obj.server_obj = new_server
            memory_list.append(memory_obj)
        Memory.objects.bulk_create(memory_list)

        ############################### 新增网卡
        """
         'network': {'status': True, 
         'detail': {'eth0': 
                        {'up': True, 'hwaddr': '00:1c:42:a5:57:7a', 'ipaddrs': '10.211.55.4', 'netmask': '255.255.255.0'}},
        'error_msg': None}
        """
        if not data['network']['status']:
            return HttpResponse('something wrong')

        network_dict = data['network']['detail']
        network_list = []
        for name, network in network_dict:
            network_obj = NIC(**network)
            network_obj.name = name
            network_obj.server_obj = new_server
            network_list.append(network_list)
        Memory.objects.bulk_create(memory_list)

























    return HttpResponse('ok')