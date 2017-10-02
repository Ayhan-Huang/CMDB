class Server:
    def __init__(self, server_obj, data):
        self.server_obj = server_obj
        self.data = data

    def process(self):
        """
        执行增删改逻辑
        :return: 
        """
        # 判断服务器信息是否更新：服务器由basic 和 board 字段组成的，字典合并；hostname属性不能变，剔除该字段
        basic_dict = self.data['basic']['detail']
        board_dict = self.data['board']['detail']
        basic_dict.update(board_dict)
        hostname = basic_dict.pop('hostname')
        server_dict = basic_dict
        print('server_dict ............. ', server_dict)

        # 利用反射，更新server_obj信息; 记录日志：先作打印显示
        record_list = []
        for field, value in server_dict.items():
            old_val = getattr(self.server_obj, field)
            new_val = value
            if old_val != new_val:
                record = '[{hostname}]的[{field}]信息，由[{old}]，更新为[{new}]'.format(
                    hostname=hostname, field=field, old=old_val, new=new_val
                )  # 这里不能用server_obj[field]... 会报错
                record_list.append(record)
                setattr(self.server_obj, field, new_val)
                self.server_obj.save()
        record_info = '\n'.join(record_list)
        print('record_info .........\n', record_info)
