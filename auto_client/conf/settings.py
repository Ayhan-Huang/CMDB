import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLUGIN = {
    'disk': 'src.plugin.disk.Disk',
    'memory': 'src.plugin.memory.Memory',
    'network': 'src.plugin.network.Network',
    # 'basic': 'src.plugin.basic.Basic',
    # 'board': 'src.plugin.board.Board',
    # 以上两项作为主机信息，必须采集，应该不应该作为用户自定义配置  --> 移至内部global_settings
}

DEBUG = True

MODE = "AGENT"  # choose from ["AGENT", "SSH", "SALTSTACK"]

API = "http://127.0.0.1:8000/api/server.html"