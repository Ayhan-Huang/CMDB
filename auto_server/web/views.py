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
        # q: 数据库查询字段； title: 前端表头； text: 前端表内容
        {
            'q': None,
            'title': '选择',
            'text': {'tpl': '<input type="checkbox" value={id}>', 'kwargs': {'id': '@id'}},
        },
        {
            'q': 'id',
            'title': 'ID',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@id'}},
        },
        {
            'q': "hostname",
            'title': '主机名',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@hostname'}},
        },
        {
            'q': "sn",
            'title': '序列号',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@sn'}},
        },
        {
            'q': "os_platform",
            'title': '系统',
            'text': {'tpl': '{a1}-{a2}', 'kwargs': {'a1': '@os_platform', 'a2': '测试前端@分离'}},
        },
        {
            'q': "os_version",
            'title': '系统版本',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@os_version'}},
        },
        {
            'q': "business_unit__name",
            'title': '业务线',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@business_unit__name'}},
        },
        {
            'q': None,
            'title': '操作',
            'text': {'tpl': '<a href="/edit/{id}/">编辑</a> | <a href=/del/{id}/>删除</a>', 'kwargs': {'id': '@id'}},
        },

    ]

    values = []
    for item in table_config:
        if item['q']:
            values.append(item['q'])

    server_list = models.Server.objects.values(*values)

    response = {
        'data_list': list(server_list),
        'table_config': table_config
    }

    return JsonResponse(response)



