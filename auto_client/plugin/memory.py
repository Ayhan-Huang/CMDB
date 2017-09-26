from lib.config import settings
import os


class Memory:
    def __init__(self):
        pass

    @classmethod  # 日后可以附加其它逻辑
    def initial(cls):
        return cls()

    def process(self, execute_cmd, debug):
        if debug:
            with open(os.path.join(settings.BASE_DIR, 'files/memory.out'), 'r', encoding='utf-8')as f:
                output = f.read()
        else:
            output = execute_cmd('命令')

        res = self.parse(output)
        return "memory info ................"

    def parse(self, output):
        """
        解析提取有效信息
        :return: 
        """
        return output