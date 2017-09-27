from lib.config import settings
import os, re


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
        # return 'disk info.........'
        return res

    def parse(self, content):
        """
               解析shell命令返回结果
               :param content: shell 命令结果
               :return:解析后的结果
               """
        response = {}
        result = []
        for row_line in content.split("\n\n\n\n"):
            result.append(row_line)
        for item in result:
            temp_dict = {}
            for row in item.split('\n'):
                if not row.strip():
                    continue
                if len(row.split(':')) != 2:
                    continue
                key, value = row.split(':')
                name = self.mega_patter_match(key)
                if name:
                    if key == 'Raw Size':
                        raw_size = re.search('(\d+\.\d+)', value.strip())
                        if raw_size:

                            temp_dict[name] = raw_size.group()
                        else:
                            raw_size = '0'
                    else:
                        temp_dict[name] = value.strip()
            if temp_dict:
                response[temp_dict['slot']] = temp_dict
        return response

    @staticmethod
    def mega_patter_match(needle):
        grep_pattern = {'Slot': 'slot', 'Raw Size': 'capacity', 'Inquiry': 'model', 'PD Type': 'pd_type'}
        for key, value in grep_pattern.items():
            if needle.startswith(key):
                return value
        return False