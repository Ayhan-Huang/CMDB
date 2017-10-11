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
        # text: tpl 字符串模板， kwargs用于替换的内容
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

    # 提取数据库查询字段
    fields= []
    for item in table_config:
        if item['q']:
            fields.append(item['q'])

    server_list = models.Server.objects.values(*fields)

    response = {
        'data_list': list(server_list), # QuerySet对象处理为可json对象
        'table_config': table_config
    }

    return JsonResponse(response)
    # 相当于return HttpResponse(json.dumps(response))


def disk(request):
    return render(request, 'disk.html')


def disk_json(request):
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
            'q': "slot",
            'title': '插槽位',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@slot'}},
        },
        {
            'q': "model",
            'title': '磁盘型号',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@model'}},
        },
        {
            'q': "capacity",
            'title': '磁盘容量GB',
            'text': {'tpl': '{a1}-{a2}', 'kwargs': {'a1': '@capacity', 'a2': '测试前端@分离'}},
        },
        {
            'q': "pd_type",
            'title': '磁盘类型',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@pd_type'}},
        },
        {
            'q': "server_obj__hostname",
            'title': '所属服务器',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@server_obj__hostname'}},
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

    disk_list = models.Disk.objects.values(*values)

    response = {
        'data_list': list(disk_list),
        'table_config': table_config
    }

    return JsonResponse(response)




