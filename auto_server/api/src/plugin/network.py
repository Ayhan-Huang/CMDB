from repository import models


class Network:
    def __init__(self, server_obj, data):
        self.server_obj = server_obj
        self.data = data

    def process(self):
        """
        执行增删改逻辑
        :return: 
        """
        latest_network_dict = self.data['network']['detail']
        # 'network': {'detail': {'eth0': {'up': True, 'hwaddr': '00:1c:42:a5:57:7a', 'ipaddrs': '10.211.55.4', 'netmask': '255.255.255.0'}}}
        for item in latest_network_dict:
            latest_network_dict[item].update({'name': item})
        former_network_dict = self.server_obj.nic.values('name', 'hwaddr', 'netmask', 'ipaddrs', 'up')
        # 如果former_network_dict为空，程序如何？--- 实测不影响

        # 列表解析也可以处理集合
        latest_slots = {i for i in latest_network_dict}
        former_slots = {i['name'] for i in former_network_dict}

        # latest_slots - former_slots 取差集 --> 新增
        # former_slots - latest_slots 取差集 --> 删除
        # latest_slots & former_slots 取交集 --> 检查属性是否有变更
        new_slots = latest_slots - former_slots
        if new_slots:
            self.add(new_slots, latest_network_dict)

        del_slots = former_slots - latest_slots
        if del_slots:
            self.delete(del_slots)

        existing_slots = latest_slots & former_slots
        if existing_slots:
            self.update(existing_slots, latest_network_dict)

    def add(self, new_slots, latest_network_dict):
        print('+++++ ', new_slots)
        nic_list = []
        record_list = []
        for slot in new_slots:
            new_nic = latest_network_dict[slot]
            nic_obj = models.NIC(**new_nic)
            nic_obj.server_obj = self.server_obj
            nic_list.append(nic_obj)
            record = '[{server}]新增网卡，名称为[{slot}]'.format(
                server=self.server_obj, slot=slot
            )
            record_list.append(record)
        models.NIC.objects.bulk_create(nic_list)
        record_info = '\n'.join(record_list)
        print('新增网卡信息..\n', record_info)

    def delete(self, del_slots):
        print('----- ', del_slots)
        record_list = []
        for slot in del_slots:
            network_obj = models.NIC.objects.filter(server_obj=self.server_obj, name=slot).first()
            record = '[{server}]删除了网卡，名称为[{slot}]'.format(
                server=self.server_obj.hostname, slot=slot
            )
            record_list.append(record)
            network_obj.delete()
        record_info = '\n'.join(record_list)
        print('删除网卡信息...\n', record_info)

    def update(self, existing_slots, latest_network_dict):
        # 通过slot拿到latest_network_dict中的latest_network
        # 通过slot拿到Disk中的network_obj，对比属性是否有变化  --> 反射
        record_list = []
        for slot in existing_slots:
            latest_network = latest_network_dict[slot]
            network_obj = models.NIC.objects.filter(name=slot, server_obj=self.server_obj).first()

            for field, value in latest_network.items():
                old_val = getattr(network_obj, field)
                new_val = value
                if old_val != new_val:
                    record = '[{server}]的网卡[{slot}]，[{field}]信息由[{old}]更新为[{new}]'.format(
                        server=self.server_obj, field=field, slot=slot, old=old_val, new=new_val
                    )
                    record_list.append(record)
                    setattr(network_obj, field, new_val)
            network_obj.save()

        record_info = '\n'.join(record_list)
        print('更新网卡...\n', record_info)