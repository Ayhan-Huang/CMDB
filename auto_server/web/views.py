from django.shortcuts import render
from .service.server import Server as ServerService

# superuser: root
# pwd:root!234

"""
程序结构：
三层架构：借鉴java
     UI层
     逻辑处理层:service
     数据访问层:models

分层：代码重用
1. 不要把代码都写在视图，逻辑复杂时，在app下创建service目录
2. 按业务逻辑分类命名
3. 具体写类，类方法

"""

def server(request):
    from django.middleware.csrf import get_token
    get_token(request)
    return render(request, 'server.html')


def server_json(request):
    service = ServerService(request)
    
    if request.method == 'GET':
        # 从数据库取服务器列表
        import time
        # 模拟网络延时
        # time.sleep(0.5)
        return service.fetch()
        
    elif request.method == 'DELETE':
        return service.delete()

    elif request.method == 'PUT':
        return service.update()


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
