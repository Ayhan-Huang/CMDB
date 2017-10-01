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
        # 拿到一个字典集合：Disk表通过slot来查找，因此，取出Disk中的一台server下的所有obj -- 处理成字典形式；
        # 对比接收到的数据，进行集合操作，如果有新slot， Disk插入数据；如果slot少了，Disk删除数据；对比字段信息是否有变化，更新

        former_memory_dict = self.server_obj.memory.values('capacity', 'slot', 'model', 'speed', 'manufacturer', 'sn')
        print(former_memory_dict)
        return 1

        # 列表解析也可以处理集合
        latest_slots = {i for i in latest_memory_dict}
        former_slots = {i['slot'] for i in former_memory_dict}

        # latest_slots - former_slots 取差集 --> 新增
        # former_slots - latest_slots 取差集 --> 删除
        # latest_slots & former_slots 取交集 --> 检查属性是否有变更
        new_slots = latest_slots - former_slots
        if new_slots:
            print('+++++ ', new_slots)
            memory_list = []
            for slot in new_slots:
                new_memory = latest_memory_dict[slot]
                memory_obj = models.Memory(**new_memory)
                memory_obj.server_obj = self.server_obj
                memory_list.append(memory_obj)
            models.Memory.objects.bulk_create(memory_list)

        del_slots = former_slots - latest_slots
        if del_slots:
            print('----- ', del_slots)
            for slot in del_slots:
                memory_obj = models.Memory.objects.filter(slot=slot).first()
                memory_obj.delete()

        existing_slots = latest_slots & former_slots
        if existing_slots:
            # 通过slot拿到latest_memory_dict中的latest_memory
            # 通过slot拿到Disk中的memory_obj，对比属性是否有变化  --> 反射
            for slot in existing_slots:
                latest_memory = latest_memory_dict[slot]
                memory_obj = models.Memory.objects.filter(slot=slot, server_obj=self.server_obj).first()

                for field, value in latest_memory.items():
                    if getattr(memory_obj, field) != latest_memory[field]:
                        setattr(memory_obj, field, value)
                memory_obj.save()