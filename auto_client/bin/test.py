import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE_DIR)

# 设置环境变量
os.environ['AUTO_CLIENT_SETTING'] = 'conf.settings'

from lib.config import settings  # 导入模块就会执行



