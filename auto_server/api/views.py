from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json, hashlib, time
from api.src.plugin import PluginManager
from django.db.models import Q
from datetime import date
from repository import models


key = 'asdgasgewfqsef'
temp_key = {
    # client_md5: timestamp  --> 过期自动清除
}

# def auth(request):
    # print(request.META)
    # token = request.META.get('HTTP_AUTH_KEY')
    # if token == key:
    #     return HttpResponse('收到')
    # else:
    #     return HttpResponse('呵呵')

    # print(request.META)

# def auth(request):
#     token = request.META.get('HTTP_AUTH_KEY')
#     print('token...',token)
#     # 6e632f8e858e07ffcc3b636a1577121b|1506983215.7659595
#     # 分割出时间字符串，用时间字符串和key进行MD5校验
#     client_md5 = token.split('|')[0]
#     now = token.split('|')[1]
#
#     temp = '{key}|{time}'.format(key=key.encode('utf-8'),time=now)
#     server_md5 = hashlib.md5(temp.encode('utf-8')).hexdigest()
#
#     if server_md5 == client_md5:
#         return HttpResponse('收到')
#     else:
#         return HttpResponse('呵呵')


def api_auth(func):
    def auth(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTH_KEY')
        print('token...',token)
        # 6e632f8e858e07ffcc3b636a1577121b|1506983215.7659595
        # 分割出时间字符串，用时间字符串和key进行MD5校验
        client_md5 = token.split('|')[0]
        timestamp = token.split('|')[1]

        temp = '{key}|{time}'.format(key=key.encode('utf-8'), time=timestamp)
        server_md5 = hashlib.md5(temp.encode('utf-8')).hexdigest()

        # 5s过期验证
        now = time.time()
        if float(timestamp) + 5 < now:
            return HttpResponse('呵呵')
        elif server_md5 != client_md5:
            return HttpResponse('呵呵')
        elif temp_key[client_md5]:
            return  HttpResponse('呵呵')
        else:
            temp_key[client_md5] = timestamp
            return func(request, *args, **kwargs)

    return auth


@api_auth
@csrf_exempt
def server(request):
    if request.method == 'GET':
        # 返回未采集主机列表：latest_date为空，或小于current_date；并且服务器状态为上线
        # 采集完成后，更新latest_date
        current_day = date.today()
        host_list = models.Server.objects.filter(
            Q(Q(latest_date=None) | Q(latest_date__date__lt=current_day)) & Q(server_status=2)
        ).values('hostname')
        host_list = list(host_list) # QuerySet对象无法被json
        return HttpResponse(json.dumps(host_list))


    elif request.method == 'POST':
    # 客户端请求头指定是json字符串，request.post无法获取内容，需要用request.body, 然后反序列化
        data = json.loads(request.body.decode('utf-8'))
        # print('data---------%r'%data)

        # 每次发过来的数据，是一台server的，根据server标识从数据库中取出server_obj; 然后再对与该server相关的硬件进行入库/修改
        if not data['basic']['status']:
            print('错误信息')
            return HttpResponse('something wrong')

        plugin_manager = PluginManager()
        response = plugin_manager.execute(data)

        return response

    # 新增服务器和硬件, 上线时，首先会录入服务器信息，因此，以下不需要
    #     """
    #    'basic': {'status': True,
    #              'detail': {'os_platform': 'linux', 'os_version': 'CentOS release 6.6 (Final)\nKernel \r on an \\m',  'hostname': 'c1.com'},
    #              'error_msg': None}
    #     """
    #     ################################## 新增服务器
    #     server_dict = data['basic']['detail']
    #     os_platform = server_dict['os_platform']
    #     os_version = server_dict['os_version']
    #
    #     new_server = Server(hostname=hostname,
    #                         os_platform=os_platform,
    #                         os_version=os_version)
    #     new_server.save()
    #
    #     ################################# 新增硬盘
    #     if not data['disk']['status']:
    #         return HttpResponse('something wrong')  # 记录错误日志
    #
    #     disk_dict = data['disk']['detail']
    #     # {'0': {'slot': '0', 'model': 'xxx', }, '1': {'slot': '0', 'model': 'xxx', }}
    #     disk_list = []
    #     for slot, disk in disk_dict.items():
    #         disk_obj = Disk(**disk)  # 批量接收字典参数用**, 批量接收列表用*
    #         disk_obj.server_obj = new_server
    #         disk_list.append(disk_obj)
    #
    #     Disk.objects.bulk_create(disk_list)
    #     print('添加硬盘信息完成')
    #
    #     ################################ 新增内存
    #     """
    #    'memory': {'status': True,
    #               'detail': {'DIMM #0': {'capacity': 1024,  'slot': 'DIMM #0',  'model': 'DRAM',  'speed': '667 MHz', 'manufacturer': 'Not Specified','sn': 'Not Specified'},
    #                         ...
    #    """
    #     if not data['memory']['status']:
    #         return HttpResponse('something wrong')
    #
    #     memory_dict = data['memory']['detail']
    #     memory_list = []
    #     for slot, memory in memory_dict.items():
    #         memory_obj = Memory(**memory)
    #         memory_obj.server_obj = new_server
    #         memory_list.append(memory_obj)
    #     Memory.objects.bulk_create(memory_list)
    #
    #     ############################### 新增网卡
    #     """
    #      'network': {'status': True,
    #      'detail': {'eth0':
    #                     {'up': True, 'hwaddr': '00:1c:42:a5:57:7a', 'ipaddrs': '10.211.55.4', 'netmask': '255.255.255.0'}},
    #     'error_msg': None}
    #     """
    #     if not data['network']['status']:
    #         return HttpResponse('something wrong')
    #
    #     network_dict = data['network']['detail']
    #     network_list = []
    #     for name, network in network_dict:
    #         network_obj = NIC(**network)
    #         network_obj.name = name
    #         network_obj.server_obj = new_server
    #         network_list.append(network_list)
    #     Memory.objects.bulk_create(memory_list)

























    return HttpResponse('ok')