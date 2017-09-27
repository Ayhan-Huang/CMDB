from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from repository.models import Disk, Server, Memory, NIC


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
        # 假设先对其中的disk进行处理,
        latest_disk_set = data['disk']['detail']
        # {'0': {'slot': '0', 'model': 'xxx', }, '1': {'slot': '0', 'model': 'xxx', }}
        # 拿到一个字典集合：Disk表通过slot来查找，因此，取出Disk中的一台server下的所有obj -- 处理成字典形式；
        # 对比接收到的数据，进行集合操作，如果有新slot， Disk插入数据；如果slot少了，Disk删除数据；对比字段信息是否有变化，更新

        former_disk_set = server_obj.disk_set.values('slot', 'model', 'capacity', 'pd_type')
        """
        [{'slot': '0', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV', 'capacity': 279.396, 'pd_type': 'SAS'}, {'slot': '1', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5AH', 'capacity': 279.396, 'pd_type': 'SAS'}, {'slot': '2', 'model': 'S1SZNSAFA01085L     Samsung SSD 850 PRO 512GB               EXM01B6Q', 'capacity': 476.939, 'pd_type': 'SATA'}, {'slot': '3', 'model': 'S1AXNSAF912433K     Samsung SSD 840 PRO Series              DXM06B0Q', 'capacity': 476.939, 'pd_type': 'SATA'}, {'slot': '4', 'model': 'S1AXNSAF303909M     Samsung SSD 840 PRO Series              DXM05B0Q', 'capacity': 476.939, 'pd_type': 'SATA'}, {'slot': '5', 'model': 'S1AXNSAFB00549A     Samsung SSD 840 PRO Series              DXM06B0Q', 'capacity': 476.939, 'pd_type': 'SATA'}]
        """
        # 处理为相同的数据结构：
        s = {}
        for item in former_disk_set:
            s[item['slot']] = item

        former_disk_set = s

        # 处理为两个集合，先对比slot；
        latest_slots = set()
        for slot in latest_disk_set:
            latest_slots.add(slot)

        former_slots = set()
        for slot in former_disk_set:
            former_slots.add(slot)

        print('l_slots',latest_slots, 'f_slots', former_slots)

        # latest_slots - former_slots 取差集 --> 新增
        # former_slots - latest_slots 取差集 --> 删除
        # latest_slots & former_slots 取交集 --> 检查属性是否有变更

        new_slots = latest_slots - former_slots
        if new_slots:
            print('+++++ ',new_slots)
            disk_list = []
            for slot in new_slots:
                new_disk = latest_disk_set[slot]
                disk_obj = Disk(**new_disk)
                disk_obj.server_obj = server_obj
                disk_list.append(disk_obj)
            Disk.objects.bulk_create(disk_list)

        del_slots = former_slots - latest_slots
        if del_slots:
            print('----- ',del_slots)
            for slot in del_slots:
                disk_obj = Disk.objects.filter(slot=slot).first()
                disk_obj.delete()

        existing_slots = latest_slots & former_slots
        if existing_slots:
            # 通过slot拿到latest_disk_set中的l_disk
            # 通过slot拿到former_disk_set中的f_disk，对比属性是否有变化
            for slot in existing_slots:
                latest_disk = latest_disk_set[slot]
                disk_obj = Disk.objects.filter(slot=slot).first()

                if disk_obj.model != latest_disk['model']:
                    disk_obj.model = latest_disk['model']
                if disk_obj.capacity != latest_disk['capacity']:
                    disk_obj.capacity = latest_disk['capacity']
                if disk_obj.pd_type != latest_disk['pd_type']:
                    disk_obj.pd_type = latest_disk['pd_type']

                disk_obj.save()

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