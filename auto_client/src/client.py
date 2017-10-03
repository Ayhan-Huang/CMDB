from .plugin import Plugin
from lib.config import settings
import requests, json, time, hashlib
from concurrent.futures import ThreadPoolExecutor


class BaseClient(object):
    def __init__(self):
        self.api = settings.API

    def execute(self):
        raise NotImplemented("子类必须实现execute方法")

    def post_data(self,data):
        key = 'asdgasgewfqsef'

        timestamp = time.time()
        temp = '{key}|{time}'.format(key=key.encode('utf-8'), time=timestamp)
        md5_str = hashlib.md5(temp.encode('utf-8')).hexdigest()
        token = '{md5_str}|{time}'.format(md5_str=md5_str, time=timestamp)
        response = requests.post(self.api, headers={"auth-key": token}, json=data)


class AgentClient(BaseClient):
    def execute(self):
        obj = Plugin()
        res = obj.execute_plugin()
        self.post_data(res)


class SshSaltClient(BaseClient):
    """
    ssh, salt模式：
    1. 获取主机列表
    2. 因为是在一台中控机上运行，采集所有服务器信息，所以需要多线程
    """
    def get_host_list(self):
        response = requests.get(self.api)
        host_list = response.text
        return json.loads(host_list)
        # return ['c1',] # 因为是测试，这里只放一个

    def task(self, host):
        obj = Plugin(host)
        res = obj.execute_plugin()
        self.post_data(res)

    def execute(self):
        # Plugin类中增加host属性
        pool = ThreadPoolExecutor(10)
        for host in self.get_host_list():
            pool.submit(self.task(host))


