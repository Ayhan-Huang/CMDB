import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLUGIN = {
    'disk': 'plugin.disk.Disk',
    'memory': 'plugin.memory.Memory',
    'network': 'plugin.network.Network',
}

DEBUG = True

MODE = "AGENT"  # choose from ["AGENT", "SSH", "SALTSTACK"]

API = "http://127.0.0.1:8000/api/server.html"