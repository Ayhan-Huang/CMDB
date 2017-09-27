import importlib
import os
from . import global_settings


class Settings(object):
    """
    目的：整合内部配置和用户自定义配置；导入global_settings + conf/settings.py
    """
    def __init__(self):
        # 导入内部配置
        for option in dir(global_settings): # dir方法，拿到模块名称空间中的所有名称
            # print(option)
            """
            NAME --> 这个是需要的，这就是为什么配置要大写
            TEST
            __builtins__
            ......
            __loader__,
            """
            if option.isupper():
                key = option
                value = getattr(global_settings, key)  # 从模块的名称空间取变量（key）的值
                # print('key:',key, 'value:value')
                setattr(self, key, value)  # 为对象增加属性

        # 导入自定义配置（从环境变量中读取配置路径）
        # 字符串路径，importlib, 剩下的同上。
        custom_settings_path = os.environ.get('AUTO_CLIENT_SETTING')
        # print(custom_settings_path) # conf.settings
        settings_module = importlib.import_module(custom_settings_path)
        for option in dir(settings_module):
            if option.isupper():
                # print(option)
                key = option
                value = getattr(settings_module, key)
                setattr(self, key, value)

settings = Settings()
# 这里是参考jango的配置文件来设计的
# 由于赋值顺序，如果有重复的配置，自定义配置会覆盖内部配置
