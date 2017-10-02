from repository import models


class Disk:
    def __init__(self, server_obj, data):
        self.server_obj = server_obj
        self.data = data

    def process(self):
        """
        执行disk的增删改逻辑
        :return: 
        """
        latest_disk_dict = self.data['disk']['detail']
        # {'0': {'slot': '0', 'model': 'xxx', }, '1': {'slot': '0', 'model': 'xxx', }}
        former_disk_dict = self.server_obj.disk_set.values('slot', 'model', 'capacity', 'pd_type')
        # [{'slot': '0', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV', 'capacity': 279.396, 'pd_type': 'SAS'},{}]
        # 列表解析也可以处理集合
        latest_slots = {i for i in latest_disk_dict}
        former_slots = {i['slot'] for i in former_disk_dict}

        # latest_slots - former_slots 取差集 --> 新增
        # former_slots - latest_slots 取差集 --> 删除
        # latest_slots & former_slots 取交集 --> 检查属性是否有变更
        new_slots = latest_slots - former_slots
        if new_slots:
            self.add(new_slots, latest_disk_dict)

        del_slots = former_slots - latest_slots
        if del_slots:
            self.delete(del_slots)

        existing_slots = latest_slots & former_slots
        if existing_slots:
            self.update(existing_slots, latest_disk_dict)

    def add(self, new_slots, latest_disk_dict):
        print('+++++ ', new_slots)
        disk_list = []
        record_list = []
        for slot in new_slots:
            new_disk = latest_disk_dict[slot]
            disk_obj = models.Disk(**new_disk)
            disk_obj.server_obj = self.server_obj
            disk_list.append(disk_obj)
            record = '[{server}]新增磁盘，槽位为[{slot}]'.format(
                server=self.server_obj.hostname, slot=slot
            )
            record_list.append(record)

        models.Disk.objects.bulk_create(disk_list)

        record_info = '\n'.join(record_list)
        print('新增磁盘信息..\n', record_info)

    def delete(self, del_slots):
        print('----- ', del_slots)
        record_list = []
        for slot in del_slots:
            disk_obj = models.Disk.objects.filter(server_obj=self.server_obj, slot=slot).first()
            record = '[{server}]删除了磁盘[{slot}]'.format(
                server=self.server_obj, slot=slot
            )
            record_list.append(record)
            disk_obj.delete()

        record_info = '\n'.join(record_list)
        print('新增磁盘信息..\n', record_info)

    def update(self, existing_slots, latest_disk_dict):
        # 通过slot拿到latest_disk_dict中的latest_disk
        # 通过slot拿到Disk中的disk_obj，对比属性是否有变化  --> 反射
        record_list = []
        for slot in existing_slots:
            latest_disk = latest_disk_dict[slot]
            disk_obj = models.Disk.objects.filter(slot=slot, server_obj=self.server_obj).first()

            for field, value in latest_disk.items():
                old_val = getattr(disk_obj, field)
                new_val = value
                print('old_val...%r' % old_val)
                print('new_val...%r' % new_val)
                # old_val...476.939
                # new_val...'476.939' 检测发现数据库数据类型和传过来数据（字符串）不一致，因而导致每次都更新
                if old_val != new_val:
                    record = '[{server}]更新了磁盘[{slot}], [{field}]信息由[{old}]更新为[{new}]'.format(
                        server=self.server_obj.hostname, slot=slot, field=field, old=old_val, new=new_val
                    )
                    record_list.append(record)
                    setattr(disk_obj, field, new_val)
            disk_obj.save()

        record_info = '\n'.join(record_list)
        print('修改磁盘信息..\n', record_info)