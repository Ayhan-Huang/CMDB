from lib.config import settings
import os
from lib import convert # 转化MB显示的


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
        # return "memory info ................"
        return res

    def parse(self, content):
        """
        解析shell命令返回结果
        :param content: shell 命令结果
        :return:解析后的结果
        """
        ram_dict = {}
        key_map = {
            'Size': 'capacity',
            'Locator': 'slot',
            'Type': 'model',
            'Speed': 'speed',
            'Manufacturer': 'manufacturer',
            'Serial Number': 'sn',

        }
        devices = content.split('Memory Device')
        for item in devices:
            item = item.strip()
            if not item:
                continue
            if item.startswith('#'):
                continue
            segment = {}
            lines = item.split('\n\t')
            for line in lines:
                if not line.strip():
                    continue
                if len(line.split(':')):
                    key, value = line.split(':')
                else:
                    key = line.split(':')[0]
                    value = ""
                if key in key_map:
                    if key == 'Size':
                        segment[key_map['Size']] = convert.convert_mb_to_gb(value, 0)
                    else:
                        segment[key_map[key.strip()]] = value.strip()

            ram_dict[segment['slot']] = segment

        return ram_dict