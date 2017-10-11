from django.db import models


class UserProfile(models.Model):
    """
    用户信息，运维管理员和业务负责人 50人
    """
    name = models.CharField('姓名', max_length=32)
    email = models.EmailField('邮箱')
    phone = models.CharField('座机', max_length=32)
    mobile = models.CharField('手机', max_length=32)

    class Meta:
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.name

# UserProfile中，运维管理员需要登录后台录入信息，而业务负责人不需要，因此额外定义表AdminInfo，
# 对于需要登录后台的人员，一对一关联到AdminInfo表中设置用户名和密码


class AdminInfo(models.Model):
    """
    用户登录： 10
    """
    user = models.OneToOneField("UserProfile")
    username = models.CharField('用户名', max_length=32)
    password = models.CharField('密码', max_length=32)


class UserGroup(models.Model):
    """
    用户组
    ID   名称
     1   组A
     2   组B
     3   组C
    用户组和用户关系表
    组ID    用户ID
     1       1
     1       2
     2       2
     2       3
     3       4
    """
    name = models.CharField(max_length=32, unique=True)
    users = models.ManyToManyField('UserProfile')

    class Meta:
        verbose_name_plural = "用户组表"

    def __str__(self):
        return self.name


class BusinessUnit(models.Model):
    """
    业务线(部门)；一台服务器属于一条业务线（如果一台服务器转部门，重装系统）
    """
    name = models.CharField('业务线', max_length=64, unique=True) # 销售，1,2
    contact = models.ForeignKey(UserGroup,related_name='c') # 业务线联系人：1
    manager = models.ForeignKey(UserGroup,related_name='m') # 运维管理人员：2
    # 实际生产中，运维管理人员、业务线联系人 和 业务线可能是多对多关系，比较混乱，解决方案：UserGroup表
    # UserGroup管理用户和分组的多对多关系，这样在BusinessUnit中，只需要contact和manager字段分别与UserGroup建立一对多关系就行了
    # related_name反向引用必须定义，否则通过UserGroup反查时会混乱。

    class Meta:
        verbose_name_plural = "业务线表"

    def __str__(self):
        return self.name


class IDC(models.Model):
    """
    机房信息
    """
    name = models.CharField('机房', max_length=32)
    floor = models.IntegerField('楼层', default=1)

    class Meta:
        verbose_name_plural = "机房表"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    资产标签，方便查找服务器
    """
    name = models.CharField('标签', max_length=32, unique=True)

    class Meta:
        verbose_name_plural = "标签表"

    def __str__(self):
        return self.name


class Server(models.Model):
    """
    服务器信息
    """
    idc = models.ForeignKey(IDC, null=True, blank=True)
    cabinet_num = models.CharField('机柜号', max_length=30, null=True, blank=True)
    cabinet_order = models.CharField('机柜中序号', max_length=30, null=True, blank=True)

    business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True)

    tags = models.ManyToManyField(Tag)

    server_status_code = (
        (1, '上架'),
        (2, '上线'),
        (3, '离线'),
        (4, '下架'),
    )
    server_status = models.IntegerField(choices=server_status_code, default=1)

    hostname = models.CharField(max_length=128, unique=True)
    sn = models.CharField('SN号', max_length=64, db_index=True)
    manufacturer = models.CharField(verbose_name='制造商', max_length=64, null=True, blank=True)
    model = models.CharField('型号', max_length=64, null=True, blank=True)

    manage_ip = models.GenericIPAddressField('管理IP', null=True, blank=True)

    os_platform = models.CharField('系统', max_length=64, null=True, blank=True)
    os_version = models.CharField('系统版本', max_length=64, null=True, blank=True)

    cpu_count = models.IntegerField('CPU个数', null=True, blank=True)
    cpu_physical_count = models.IntegerField('CPU物理个数', null=True, blank=True)
    cpu_model = models.CharField('CPU型号', max_length=128, null=True, blank=True)

    create_at = models.DateTimeField(auto_now_add=True, blank=True)
    latest_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "服务器表"

    def __str__(self):
        return self.hostname


class Disk(models.Model):
    """
    硬盘信息
    """
    slot = models.CharField('插槽位', max_length=8)
    model = models.CharField('磁盘型号', max_length=32)
    capacity = models.FloatField('磁盘容量GB')
    pd_type = models.CharField('磁盘类型', max_length=32)
    # server_obj = models.ForeignKey('Server',related_name='disk')
    server_obj = models.ForeignKey('Server')
    # 测试发现，related_name='disk' 相当于在Server表中增加了一个disk字段，来获取disk集合；
    # 这样就不需要disk_set来反向查询了

    class Meta:
        verbose_name_plural = "硬盘表"

    def __str__(self):
        return self.slot


class NIC(models.Model):
    """
    网卡信息
    """
    name = models.CharField('网卡名称', max_length=128)
    hwaddr = models.CharField('网卡mac地址', max_length=64)
    netmask = models.CharField(max_length=64)
    ipaddrs = models.CharField('ip地址', max_length=256)
    up = models.BooleanField(default=False)
    server_obj = models.ForeignKey('Server',related_name='nic')


    class Meta:
        verbose_name_plural = "网卡表"

    def __str__(self):
        return self.name


class Memory(models.Model):
    """
    内存信息
    """
    slot = models.CharField('插槽位', max_length=32)
    manufacturer = models.CharField('制造商', max_length=32, null=True, blank=True)
    model = models.CharField('型号', max_length=64)
    capacity = models.FloatField('容量', null=True, blank=True)
    sn = models.CharField('内存SN号', max_length=64, null=True, blank=True)
    speed = models.CharField('速度', max_length=16, null=True, blank=True)

    server_obj = models.ForeignKey('Server',related_name='memory')


    class Meta:
        verbose_name_plural = "内存表"

    def __str__(self):
        return self.slot


class ServerRecord(models.Model):
    """
    服务器变更记录,creator为空时，表示是资产汇报的数据。
    """
    server_obj = models.ForeignKey('Server', related_name='ar')
    content = models.TextField(null=True)
    creator = models.ForeignKey('UserProfile', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "资产记录表"

    def __str__(self):
        return self.server_obj.hostname


class ErrorLog(models.Model):
    """
    错误日志,如：agent采集数据错误 或 运行错误
    """
    server_obj = models.ForeignKey('Server', null=True, blank=True)
    title = models.CharField(max_length=16)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "错误日志表"

    def __str__(self):
        return self.title
