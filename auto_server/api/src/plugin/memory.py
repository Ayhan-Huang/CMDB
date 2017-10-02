from repository import models


class Memory:
    def __init__(self, server_obj, data):
        self.server_obj = server_obj
        self.data = data

    def process(self):
        """
        执行增删改逻辑
        :return: 
        """
        latest_memory_dict = self.data['memory']['detail']
        # {'DIMM #0': {'capacity': 1024, 'slot': 'DIMM #0', 'model': 'DRAM', 'speed': '667 MHz', 'manufacturer': 'Not Specified', 'sn': 'Not Specified'}
        former_memory_dict = self.server_obj.memory.values('capacity', 'slot', 'model', 'speed', 'manufacturer', 'sn')
        # 如果former_memory_dict为空，程序如何？--- 实测不影响

        # 列表解析也可以处理集合
        latest_slots = {i for i in latest_memory_dict}
        former_slots = {i['slot'] for i in former_memory_dict}

        # latest_slots - former_slots 取差集 --> 新增
        # former_slots - latest_slots 取差集 --> 删除
        # latest_slots & former_slots 取交集 --> 检查属性是否有变更
        new_slots = latest_slots - former_slots
        if new_slots:
            self.add(new_slots, latest_memory_dict)

        del_slots = former_slots - latest_slots
        if del_slots:
            self.delete(del_slots)

        existing_slots = latest_slots & former_slots
        if existing_slots:
            self.update(existing_slots, latest_memory_dict)

    def add(self, new_slots, latest_memory_dict):
        print('+++++ ', new_slots)
        memory_list = []
        record_list = []
        for slot in new_slots:
            new_memory = latest_memory_dict[slot]
            memory_obj = models.Memory(**new_memory)
            memory_obj.server_obj = self.server_obj
            memory_list.append(memory_obj)
            record = '[{server}]新增内存，槽位为[{slot}]'.format(
                server=self.server_obj, slot=slot
            )
            record_list.append(record)
        models.Memory.objects.bulk_create(memory_list)
        record_info = '\n'.join(record_list)
        print('新增内存信息..\n', record_info)

    def delete(self, del_slots):
        print('----- ', del_slots)
        record_list = []
        for slot in del_slots:
            memory_obj = models.Memory.objects.filter(server_obj=self.server_obj, slot=slot).first()
            record = '[{server}]删除了内存，插槽为[{slot}]'.format(
                server=self.server_obj.hostname, slot=slot
            )
            record_list.append(record)
            memory_obj.delete()
        record_info = '\n'.join(record_list)
        print('删除内存信息...\n', record_info)

    def update(self, existing_slots, latest_memory_dict):
        # 通过slot拿到latest_memory_dict中的latest_memory
        # 通过slot拿到Disk中的memory_obj，对比属性是否有变化  --> 反射
        record_list = []
        for slot in existing_slots:
            latest_memory = latest_memory_dict[slot]
            memory_obj = models.Memory.objects.filter(slot=slot, server_obj=self.server_obj).first()

            for field, value in latest_memory.items():
                old_val = getattr(memory_obj, field)
                new_val = value
                if old_val != new_val:
                    record = '[{server}]的内存[{slot}]，[{field}]信息由[{old}]更新为[{new}]'.format(
                        server=self.server_obj, field=field, slot=slot, old=old_val, new=new_val
                    )
                    record_list.append(record)
                    setattr(memory_obj, field, new_val)
            memory_obj.save()

        record_info = '\n'.join(record_list)
        print('更新内存...\n', record_info)