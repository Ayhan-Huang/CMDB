import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLUGIN = {
    'disk': 'src.plugin.disk.Disk',
    'memory': 'src.plugin.memory.Memory',
    'network': 'src.plugin.network.Network',
    'basic': 'src.plugin.basic.Basic',
}

DEBUG = True

MODE = "AGENT"  # choose from ["AGENT", "SSH", "SALTSTACK"]

API = "http://127.0.0.1:8000/api/server.html"