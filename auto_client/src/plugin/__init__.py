from lib.config import settings
# 导入模块就会执行实例化，整合配置
import importlib, subprocess, traceback


class Plugin(object):
    def __init__(self, host=None):
        # 这里将settings中的配置在构造函数赋值作为对象属性，更易于管理
        self.host = host
        self.mode = settings.MODE
        self.plugin = settings.PLUGIN
        self.debug = settings.DEBUG

    def execute_plugin(self):
        data = {}  # 服务器信息采集结果
        for k, v in self.plugin.items():
            info = {'status': True, 'detail': None, "error_msg": None}
            # 分离模块路径 和 类名：
            # 'plugin.disk.Disk'  --> 模块路径'plugin.disk' 类名 'Disk' （结果都是字符串）
            # 通过字符串路径导入模块 importlib
            # 通过反射获取模块中的类（从名称空间中获取名称的值）
            module_name, cls_name = v.rsplit('.', maxsplit=1)
            module = importlib.import_module(module_name)
            cls = getattr(module, cls_name)

            if hasattr(cls, 'initial'):
                obj = cls.initial()
            else:
                obj = cls()

            try:
                res = obj.process(self.execute_cmd, self.debug)
                info['detail'] = res
            except Exception:
                info['status'] = False
                info['error_msg'] = traceback.format_exc()

            data[k] = info
            # 服务器采集信息结果采用字典嵌套的形式，key是插件（即服务器被检测硬件），value是检测结果或错误信息
            # {
            # 'disk': {'status': True, 'detail': 'disk info.........', 'error_msg': None},
            # 'memory': {'status': True, 'detail': 'memory info ................', 'error_msg': None},
            # 'network': {'status': True, 'detail': 'network info ..................', 'error_msg': None}
            # }

        print(data)
        return data

    def execute_cmd(self,cmd):
        """
        执行命令返回结果；
        设计为兼容多种方式（agent, ssh, saltstack)，只需要在配置指定方式(settings.MODE)，这里读取配置，以对应的方式执行命令
        :param cmd: cmd由插件对象在process方法中执行execute_cmd手动传入
        :return: 
        """
        if self.mode == 'AGENT':
            res = subprocess.getoutput(cmd)
        elif self.mode == 'SSH': # paramiko进行SSH连接，执行命令
            pass
        elif self.mode == 'SALTSTACK':
            pass
        else:
            raise Exception('未指定的模式，可选模式为 "AGENT", "SSH", "SALTSTACK"')

        return res

# 改为面向对象的方式
