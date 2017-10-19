# 前端搜索配置
search_config = [
    {'name': 'server_status', 'title': '状态', 'type': 'select', 'choice_name': 'server_status_code'},
    {'name': 'hostname__contains', 'title': '主机名', 'type': 'input'},
    {'name': 'cabinet_num', 'title': '机柜号', 'type': 'input'},
    # type键用于前端判断搜索框类型
    # 对于下拉框类型，提供choice_name键，以便前端从response.global_choices_dict.choice_name中获取静态字段
]

# 前端table数据展示配置
table_config = [
    # q: 数据库查询字段； title: 前端表头； text: 前端表内容
    # text: tpl 含占位符的字符串模板， kwargs用于替换的内容，如果@开头，用@分离的数据库字段查询结果替换占位符，否则直接替换
    {
        'q': None,
        'title': '选择',
        'display': True,
        'text': {'tpl': '<input type="checkbox" value={id}>', 'kwargs': {'id': '@id'}},
        'attr': {'nid': '@id'}
    },
    {
        'q': 'id',
        'title': 'ID',
        'display': False,
        'text': {'tpl': '{a1}', 'kwargs': {'a1': '@id'}},
        'attr': {'nid': '@id'}
    },
    {
        'q': "hostname",
        'title': '主机名',
        'display': True,
        'text': {'tpl': '{a1}', 'kwargs': {'a1': '@hostname'}},
        'attr': {'edit': True, 'origin': '@hostname', 'edit-type': 'input', 'name': 'hostname'}
    },
    {
        'q': "sn",
        'title': '序列号',
        'display': True,
        'text': {'tpl': '{a1}', 'kwargs': {'a1': '@sn'}},
        'attr': {'origin': "@sn", }
    },
    {
        'q': "os_platform",
        'title': '系统',
        'display': True,
        'text': {'tpl': '{a1}-{a2}', 'kwargs': {'a1': '@os_platform', 'a2': '测试前端@分离'}},
        'attr': {'edit': True, 'origin': '@os_platform', 'name': 'os_platform', 'edit-type': 'input'}
    },
    {
        'q': "os_version",
        'title': '系统版本',
        'display': True,
        'text': {'tpl': '{a1}', 'kwargs': {'a1': '@os_version'}},
        'attr': {'edit': True, 'origin': '@os_version', 'name': 'os_version', 'edit-type': 'input'}
    },
    {
        'q': "business_unit__name",
        'title': '业务线',
        'display': True,
        'text': {'tpl': '{a1}', 'kwargs': {'a1': '@business_unit__name'}},
        'attr': {'edit': True, 'origin': '@business_unit__name', 'name': 'business_unit__name', 'edit-type': 'input'}
    },
    {
        'q': "server_status",
        'title': '状态',
        'display': True,
        'text': {'tpl': '{a1}', 'kwargs': {'a1': '@@server_status'}},
        # 定义：前端检测到@@，则从静态字段中取出对应的状态说明
        'attr': {'edit': True, 'origin': '@server_status_id', 'name': 'server_status_id', 'edit-type': 'select',
                 'choice_name': 'server_status_code',
                 'server_status': '@server_status'}
    },
    {
        'q': None,
        'title': '操作',
        'display': True,
        'text': {'tpl': '<a href="/edit/{id}/">编辑</a> | <a href=/del/{id}/>删除</a>', 'kwargs': {'id': '@id'}},
        'attr': {'origin': '@id'}
    },

]