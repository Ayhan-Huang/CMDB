# 这里不需要进行配置合并，django自己作
# 根据settings中的字典，导入模块，实例化，处理请求
from django.conf import settings
import importlib
from django.shortcuts import HttpResponse


class PluginManager:
    def __init__(self, server_obj, data):
        self.plugin = settings.PLUGIN
        self.server_obj = server_obj
        self.data = data

    def execute(self):
        # 判断服务器信息是否更新：服务器由basic 和 board 字段组成的，字典合并；hostname属性不能变，剔除该字段
        basic_dict = self.data['basic']['detail']
        board_dict = self.data['board']['detail']
        basic_dict.update(board_dict)
        hostname = basic_dict.pop('hostname')
        server_dict = basic_dict
        print('server_dict ............. ', server_dict)

        # 利用反射，更新server_obj信息; 记录日志：先作打印显示
        record_list = []
        for field, value in server_dict.items():
            if getattr(self.server_obj, field) != server_dict[field]:
                record = '[{hostname}]的[{field}]信息，由[{old}]，更新为[{new}]'.format(
                    hostname=hostname, field=field, old='fuck', new=server_dict[field]
                )  # 这里不能用server_obj[field]... 会报错
                record_list.append(record)
                setattr(self.server_obj, field, value)
        record_info = '\n'.join(record_list)
        print('record_info .........\n', record_info)

        # 其余插件都是可插拔的，在下面执行
        for k, v in self.plugin.items():
            # 'disk': 'api.src.plugin.disk.Disk',
            module_path, cls_name = v.rsplit('.', maxsplit=1)
            module = importlib.import_module(module_path)
            cls = getattr(module, cls_name)
            print('cls----', cls)
            obj = cls(self.server_obj, self.data)  # TypeError: object() takes no parameters
            obj.process()
            # except Exception as e:
            #     print('error..',e)
            #     raise Exception('something wrong...')

        return HttpResponse('....')