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
        # 拿到一个字典集合：Disk表通过slot来查找，因此，取出Disk中的一台server下的所有obj -- 处理成字典形式；
        # 对比接收到的数据，进行集合操作，如果有新slot， Disk插入数据；如果slot少了，Disk删除数据；对比字段信息是否有变化，更新

        former_disk_dict = self.server_obj.disk_set.values('slot', 'model', 'capacity', 'pd_type')
        """
        [{'slot': '0', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV', 'capacity': 279.396, 'pd_type': 'SAS'}, {'slot': '1', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5AH', 'capacity': 279.396, 'pd_type': 'SAS'}, {'slot': '2', 'model': 'S1SZNSAFA01085L     Samsung SSD 850 PRO 512GB               EXM01B6Q', 'capacity': 476.939, 'pd_type': 'SATA'}, {'slot': '3', 'model': 'S1AXNSAF912433K     Samsung SSD 840 PRO Series              DXM06B0Q', 'capacity': 476.939, 'pd_type': 'SATA'}, {'slot': '4', 'model': 'S1AXNSAF303909M     Samsung SSD 840 PRO Series              DXM05B0Q', 'capacity': 476.939, 'pd_type': 'SATA'}, {'slot': '5', 'model': 'S1AXNSAFB00549A     Samsung SSD 840 PRO Series              DXM06B0Q', 'capacity': 476.939, 'pd_type': 'SATA'}]
        """

        # 列表解析也可以处理集合
        latest_slots = {i for i in latest_disk_dict}
        former_slots = {i['slot'] for i in former_disk_dict}

        # latest_slots - former_slots 取差集 --> 新增
        # former_slots - latest_slots 取差集 --> 删除
        # latest_slots & former_slots 取交集 --> 检查属性是否有变更

        new_slots = latest_slots - former_slots
        if new_slots:
            print('+++++ ', new_slots)
            disk_list = []
            for slot in new_slots:
                new_disk = latest_disk_dict[slot]
                disk_obj = models.Disk(**new_disk)
                disk_obj.server_obj = self.server_obj
                disk_list.append(disk_obj)
            models.Disk.objects.bulk_create(disk_list)

        del_slots = former_slots - latest_slots
        if del_slots:
            print('----- ', del_slots)
            for slot in del_slots:
                disk_obj = models.Disk.objects.filter(slot=slot).first()
                disk_obj.delete()

        existing_slots = latest_slots & former_slots
        if existing_slots:
            # 通过slot拿到latest_disk_dict中的latest_disk
            # 通过slot拿到Disk中的disk_obj，对比属性是否有变化  --> 反射
            for slot in existing_slots:
                latest_disk = latest_disk_dict[slot]
                disk_obj = models.Disk.objects.filter(slot=slot, server_obj=self.server_obj).first()

                for field, value in latest_disk.items():
                    if getattr(disk_obj, field) != latest_disk[field]:
                        setattr(disk_obj, field, value)
                disk_obj.save()
