# 这里不需要进行配置合并，django自己作
# 根据settings中的字典，导入模块，实例化，处理请求
from django.conf import settings
import importlib, json
from django.shortcuts import HttpResponse
from repository import models
from api.src.plugin import server


class PluginManager:
    def __init__(self):
        self.plugin = settings.PLUGIN

    def execute(self, data):
        """
        改写为插拔式，执行任何操作，都需要两个参数：server_obj ,data
        先配置，再利用反射，执行。。。
        :param data: 
        :return: code: 1, 执行成功； 2, 服务器不存在； 3, 出现错误
        """
        ret = {'code': 1, 'msg': None}

        hostname = data['basic']['detail']['hostname']
        server_obj = models.Server.objects.filter(hostname=hostname).first()

        if not server_obj:
            ret['code'] = 2
            return ret

        # server信息，客户端一定会传过来，而且也必须处理，因此不能设计为可插拔
        # 其余插件都是可插拔设计，在for循环中执行
        edit_server = server.Server(server_obj, data)
        edit_server.process()
        # TypeError: object() takes no parameters ？？？
        # TypeError: object() takes no parameters
        # ！！！构造器函数__init__ 拼写为 __int__；改过来后，重启服务，自动变为__int__，诡异；关掉所有脚本，重启pycharm正常了。。。

        for k, v in self.plugin.items():
            # 'disk': 'api.src.plugin.disk.Disk',
            # try:
            module_path, cls_name = v.rsplit('.', maxsplit=1)
            module = importlib.import_module(module_path)
            cls = getattr(module, cls_name)
            print('cls----', cls)
            obj = cls(server_obj, data)
            obj.process()
            # except Exception as e:
            #     print('error..',e)
            #     ret['code'] = 3

        return HttpResponse(json.dumps(ret))