from lib.config import settings
import os


class Disk:
    def __init__(self):
        pass

    @classmethod  # 日后可以附加其它逻辑
    def initial(cls):
        return cls()

    def process(self,execute_cmd,debug):
        if debug: # 如果是debug模式，直接读取一段文本
            with open(os.path.join(settings.BASE_DIR, 'files/disk.out'), 'r', encoding='utf-8')as f:
                output = f.read()
        else:
            output = execute_cmd('ifconfig')

        res = self.parse(output)
        return 'disk info.........'

    def parse(self, output):
        """
        解析提取有效信息
        :return: 
        """
        return output