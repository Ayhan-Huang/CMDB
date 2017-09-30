# 需要在这里作逻辑判断，MODE
# MODE不同，实例化不同对象
# 每个对象执行Plugin，只不过ssh, salt多一个步骤：获取host_list

from .client import AgentClient, SshSaltClient


def start():
    from lib.config import settings
    if settings.MODE == 'AGENT':
        obj = AgentClient()
    elif settings.MODE == 'SSH'or settings.MODE == 'SALT':
        obj = SshSaltClient()
    else:
        raise Exception('MODE ERROR!')
    obj.execute()
