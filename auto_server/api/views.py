from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from repository.models import Disk, Server


@csrf_exempt
def server(request):
    # 客户端请求头指定是json字符串，request.post无法获取内容，需要用request.body, 然后反序列化
    data = json.loads(request.body.decode('utf-8'))
    print('data---------%r'%data)

    # 每次发过来的数据，是一台server的，根据server标识从数据库中取出server_obj; 然后再对与该server相关的硬件进行入库/修改
    if not data['basic']['status']:
        print('错误信息')
        return HttpResponse('something wrong')

    hostname = data['basic']['detail']['hostname']
    server_obj = Server.objects.filter(hostname=hostname).first()

    if server_obj: # 取出其相关的硬件信息
        # 假设先对其中的disk进行处理,
        new_disk_set = data['disk']['detail']
        # {'0': {'slot': '0', 'model': 'xxx', }, '1': {'slot': '0', 'model': 'xxx', }}
        # 拿到一个字典集合：Disk表通过slot来查找，因此，取出Disk中的一台server下的所有obj -- 处理成字典形式；
        # 对比接收到的数据，进行集合操作，如果有新slot， Disk插入数据；
        old_disk_set = server_obj.disk_set.values('slot', 'model', 'capacity', 'pd_type')
        print(old_disk_set)
    else: # 新增服务器和硬件
        """ 
       'basic': {'status': True, 
                 'detail': {'os_platform': 'linux',
                            'os_version': 'CentOS release 6.6 (Final)\nKernel \r on an \\m',
                            'hostname': 'c1.com'},
                 'error_msg': None}
        """
        # 新增服务器
        server_dict = data['basic']['detail']
        os_platform = server_dict['os_platform']
        os_version = server_dict['os_version']

        new_server = Server(hostname=hostname,
                            os_platform=os_platform,
                            os_version=os_version)
        new_server.save()

        # 新增硬盘
        disk_dict = data['disk']['detail']
        # {'0': {'slot': '0', 'model': 'xxx', }, '1': {'slot': '0', 'model': 'xxx', }}
        disk_list = []

        for slot, disk in disk_dict.items():
            disk_obj = Disk(**disk)  # 批量接收字典参数用**, 批量接收列表用*
            disk_obj.server_obj = new_server
            disk_list.append(disk_obj)

        Disk.objects.bulk_create(disk_list)
        print('添加硬盘信息完成')
























    return HttpResponse('ok')