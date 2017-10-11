from django.shortcuts import render
from repository import models
from django.http import JsonResponse


def server(request):
    return render(request, 'server.html')


def server_json(request):
    # 从数据库取服务器列表
    import time
    # 模拟网络延时
    time.sleep(0.5)

    table_config = [
        {
            'q': "hostname",
            'title': '主机名',
        },
        {
            'q': "sn",
            'title': '序列号',
        },
        {
            'q': "os_platform",
            'title': '系统'
        }
    ]

    values = []
    for item in table_config:
        values.append(item['q'])

    server_list = models.Server.objects.values(*values)

    response = {
        'data_list': list(server_list),
        'table_config': table_config
    }

    return JsonResponse(response)



