import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE_DIR)

# 设置环境变量
os.environ['AUTO_CLIENT_SETTING'] = 'conf.settings'

# ssh/salt模式，需要先连接API，获取主机列表，然后循环执行;
# 这些逻辑不要写在run中，run只是一个入口

if __name__ == "__main__":
    # from src.plugin import Plugin
    # obj = Plugin()
    # res = obj.execute_plugin()
    # print(res)
    from src import script
    script.start()


# requests.post(API, data=data)

