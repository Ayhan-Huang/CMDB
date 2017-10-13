from django.shortcuts import render
from repository import models
from django.http import JsonResponse
from utils.page import Pagination

# superuser: root
# pwd:root!234

def server(request):
    return render(request, 'server.html')


def server_json(request):
    # 从数据库取服务器列表
    import time
    # 模拟网络延时
    time.sleep(0.5)

    table_config = [
        # q: 数据库查询字段； title: 前端表头； text: 前端表内容
        # text: tpl 含占位符的字符串模板， kwargs用于替换的内容，如果@开头，用@分离的数据库字段查询结果替换占位符，否则直接替换
        {
            'q': None,
            'title': '选择',
            'display': True,
            'text': {'tpl': '<input type="checkbox" value={id}>', 'kwargs': {'id': '@id'}},
            'attr': {'edit': True, 'origin': '@id'}
        },
        {
            'q': 'id',
            'title': 'ID',
            'display': False,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@id'}},
            'attr': {'edit': True, 'origin': '@id'}
        },
        {
            'q': "hostname",
            'title': '主机名',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@hostname'}},
            'attr': {'edit': False, 'origin': '@id'}
        },
        {
            'q': "sn",
            'title': '序列号',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@sn'}},
            'attr': {'edit': False, 'origin': '@id'}
        },
        {
            'q': "os_platform",
            'title': '系统',
            'display': True,
            'text': {'tpl': '{a1}-{a2}', 'kwargs': {'a1': '@os_platform', 'a2': '测试前端@分离'}},
            'attr': {'edit': True, 'origin': '@id'}
        },
        {
            'q': "os_version",
            'title': '系统版本',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@os_version'}},
            'attr': {'edit': True, 'origin': '@id'}
        },
        {
            'q': "business_unit__name",
            'title': '业务线',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@business_unit__name'}},
            'attr': {'edit': True, 'origin': '@id'}
        },
        {
            'q': "server_status",
            'title': '状态',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@@server_status'}},
            # 定义：前端检测到@@，则从静态字段中取出对应的状态说明
            'attr': {'edit': True, 'origin': '@id'}
        },
        {
            'q': None,
            'title': '操作',
            'display': True,
            'text': {'tpl': '<a href="/edit/{id}/">编辑</a> | <a href=/del/{id}/>删除</a>', 'kwargs': {'id': '@id'}},
            'attr': {'edit': True, 'origin': '@id'}
        },

    ]

    # 提取数据库查询字段
    fields= []
    for item in table_config:
        if item['q']:
            fields.append(item['q'])

    # 获取请求页码并实例化分页器
    current_page = request.GET.get('pageNum')
    total_item_count = models.Server.objects.all().count()
    paginator = Pagination(current_page=current_page,
                           total_item_count=total_item_count,
                           per_page_count=2)

    server_list = models.Server.objects.values(*fields)[paginator.start: paginator.end]

    response = {
        'data_list': list(server_list), # QuerySet对象处理为可json对象
        'table_config': table_config,
        'global_choices_dict': {
            'server_status_code': models.Server.server_status_code,  # 静态字段可能不止一个，因此用一个大字典封装
        },
        'page_html': paginator.page_html_js()
    }

    return JsonResponse(response)
    # 相当于return HttpResponse(json.dumps(response))
    # JsonResponse如果接收列表，默认会报错，因为列表不规范，没有key，不能包含状态等详细信息。


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



def xx(server_list):
    for row in server_list:
        for item in models.Server.server_status_code:
            if item[0] == row['server_status']:
                row['server_status_id_name'] = item[1]
                break
        yield row

def test(request):
    server_list = models.Server.objects.all().values('hostname', 'server_status')
    return render(request, 'test.html', {'server_list': xx(server_list)})


