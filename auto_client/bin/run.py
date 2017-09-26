import requests
import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE_DIR)

# 设置环境变量
os.environ['AUTO_CLIENT_SETTING'] = 'conf.settings'

if __name__ == "__main__":
    from plugin import Plugin
    obj = Plugin()
    res = obj.execute_plugin()
    print(res)


# requests.post(API, data=data)

