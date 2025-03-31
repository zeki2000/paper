"""
数据模型模块，包含完整的数据库表结构设计：
1. 用户与登录模块
   - 用户表(User)
   - 验证码模型(VerificationCode)
2. 普通用户(C端)模块
   - 用户信息表(UserInfo)
   - 地址簿表(AddressBook)
   - 实名认证表(UserCertification)
3. 家政服务提供者(B端)模块
   - 服务者信息表(ServiceProviderInfo)
   - 资质证书表(Certification)
   - 服务表(Service)
4. 订单与支付模块
   - 订单表(Order)
   - 支付记录表(Payment)
5. 售后服务与评价模块
   - 售后工单表(AfterSales)
   - 评价表(Review)
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator, MaxValueValidator
import random
from datetime import timedelta
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class VerificationCode(models.Model):
    """
    短信验证码模型
    字段:
    - phone: 手机号
    - code: 6位数字验证码
    - created_at: 创建时间
    方法:
    - generate_code: 生成并保存验证码
    """
    phone = models.CharField(max_length=11, verbose_name='手机号')
    code = models.CharField(max_length=6, verbose_name='验证码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'verification_code'
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        
    @classmethod
    def generate_code(cls, phone):
        """
        生成并保存验证码
        参数:
            phone: 手机号
        返回:
            生成的6位数字验证码
        """
        # 删除过期验证码
        cls.objects.filter(
            created_at__lt=timezone.now()-timedelta(minutes=5)
        ).delete()
        
        # 生成6位随机数字
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # 保存验证码
        cls.objects.create(phone=phone, code=code)
        
        return code

class User(AbstractUser):
    """
    用户模型，继承自Django的AbstractUser
    扩展字段:
    - phone: 手机号(登录账号)，AES-256加密存储
    - role: 用户角色(C端用户/B端服务者/管理员)
    - status: 账户状态(正常/冻结/注销)
    """
    ROLE_CHOICES = (
        ('C', '普通用户'),
        ('B', '服务提供者'), 
        ('ADMIN', '管理员')
    )
    STATUS_CHOICES = (
        ('正常', '正常'),
        ('冻结', '冻结'),
        ('注销', '注销')
    )
    
    phone = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='手机号',
        validators=[
            RegexValidator(
                regex=r'^1[3-9]\d{9}$',
                message='请输入正确的手机号码'
            )
        ]
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='C',
        verbose_name='用户角色'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='正常',
        verbose_name='账户状态'
    )
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

class UserInfo(models.Model):
    """
    用户信息表(C端用户)
    字段:
    - user: 关联用户账号
    - nickname: 用户昵称(2-10字符)
    - gender: 性别
    - birthday: 出生日期
    - avatar: 头像URL(JPG/PNG ≤2MB)
    """
    GENDER_CHOICES = (
        ('男', '男'),
        ('女', '女'),
        ('未知', '未知')
    )
    
    ADJECTIVES = ['快乐的', '聪明的', '勇敢的', '优雅的', '活泼的', '安静的', '热情的', '潇洒的']
    NOUNS = ['可乐', '螺蛳粉', '炸鸡', '舒芙蕾', '米粉', '脏脏包', '凤爪', '狮子头']
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户账号')
    nickname = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[\w\u4e00-\u9fa5]{2,10}$',
                message='昵称只能包含中文、字母和数字，长度2-10位'
            )
        ],
        verbose_name='昵称'
    )
    
    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = f"{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}"
        if not self.avatar:
            avatar_num = random.randint(1, 6)
            self.avatar = f'avatars/avatar{avatar_num}.jpg'
        super().save(*args, **kwargs)
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='未知',
        verbose_name='性别'
    )
    birthday = models.DateField(null=True, blank=True, verbose_name='出生日期')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='头像',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'png']),
            MaxValueValidator(2*1024*1024)  # 2MB
        ]
    )
    
    class Meta:
        db_table = 'user_info'
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

class AddressBook(models.Model):
    """
    地址簿表
    字段:
    - user: 关联用户账号
    - address: 服务地址(精确到楼栋门牌号)
    - is_default: 是否默认地址(最多5条)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    address = models.CharField(max_length=255, verbose_name='服务地址')
    is_default = models.BooleanField(default=False, verbose_name='默认地址')
    
    class Meta:
        db_table = 'address_book'
        verbose_name = '地址簿'
        verbose_name_plural = '地址簿'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_address'
            )
        ]

class UserCertification(models.Model):
    """
    实名认证表
    字段:
    - user: 关联用户账号
    - real_name: 真实姓名
    - id_card: 身份证号(AES-256加密)
    - status: 认证状态
    """
    STATUS_CHOICES = (
        ('待审核', '待审核'),
        ('通过', '通过'),
        ('驳回', '驳回')
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    real_name = models.CharField(max_length=50, verbose_name='真实姓名')
    id_card = models.CharField(max_length=18, verbose_name='身份证号')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='待审核',
        verbose_name='认证状态'
    )
    
    class Meta:
        db_table = 'user_certification'
        verbose_name = '实名认证'
        verbose_name_plural = '实名认证'

class ServiceProviderInfo(models.Model):
    """
    服务者信息表(B端)
    字段:
    - user: 关联用户账号
    - service_area: 服务范围(行政区域或半径≤10公里)
    - introduction: 服务者简介(≤100字符)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    service_area = models.CharField(max_length=100, verbose_name='服务范围')
    introduction = models.CharField(max_length=100, verbose_name='简介')
    
    class Meta:
        db_table = 'service_provider_info'
        verbose_name = '服务者信息'
        verbose_name_plural = '服务者信息'

class Certification(models.Model):
    """
    资质证书表
    字段:
    - provider: 关联服务者
    - certificate_url: 证书存储路径(PDF/JPG)
    - status: 审核状态
    """
    STATUS_CHOICES = (
        ('待审核', '待审核'),
        ('通过', '通过'),
        ('驳回', '驳回')
    )
    
    provider = models.ForeignKey(ServiceProviderInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='服务者')
    certificate_url = models.FileField(
        upload_to='certificates/',
        verbose_name='证书文件',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg'])
        ]
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='待审核',
        verbose_name='审核状态'
    )
    
    class Meta:
        db_table = 'certification'
        verbose_name = '资质证书'
        verbose_name_plural = '资质证书'

class ServiceCategory(models.Model):
    """
    服务类别模型
    字段:
    - name: 类别名称
    - icon: 图标代码
    """
    name = models.CharField(max_length=50, verbose_name='类别名称')
    icon = models.CharField(max_length=50, verbose_name='图标代码')
    
    class Meta:
        db_table = 'service_category'
        verbose_name = '服务类别'
        verbose_name_plural = '服务类别'

class Service(models.Model):
    """
    服务项目模型
    字段:
    - name: 服务名称(≤20字符)
    - provider: 关联服务者
    - price: 服务价格(10-500元)
    - service_type: 服务类型(保洁/维修)
    """
    SERVICE_TYPE_CHOICES = (
        ('保洁', '保洁'),
        ('维修', '维修')
    )
    
    name = models.CharField(max_length=50, verbose_name='服务名称')
    provider = models.ForeignKey(ServiceProviderInfo, on_delete=models.CASCADE, null=True, blank=True, default=None, verbose_name='服务者')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='价格',
        validators=[
            MinValueValidator(10),
            MaxValueValidator(500)
        ]
    )
    service_type = models.CharField(
        max_length=10,
        choices=SERVICE_TYPE_CHOICES,
        default='保洁',
        verbose_name='服务类型'
    )
    
    class Meta:
        db_table = 'service'
        verbose_name = '服务项目'
        verbose_name_plural = '服务项目'

class Order(models.Model):
    """
    订单表
    字段:
    - user: 下单用户
    - provider: 服务者
    - service: 服务项目
    - address: 服务地址(外键)
    - status: 订单状态
    - start_time: 服务开始时间
    - end_time: 服务结束时间
    """
    STATUS_CHOICES = (
        ('待支付', '待支付'),
        ('已支付', '已支付'),
        ('已取消', '已取消'),
        ('已完成', '已完成')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    provider = models.ForeignKey(ServiceProviderInfo, on_delete=models.CASCADE, verbose_name='服务者')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='服务项目')
    address = models.ForeignKey(AddressBook, on_delete=models.CASCADE, verbose_name='服务地址')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='待支付',
        verbose_name='订单状态'
    )
    start_time = models.DateTimeField(null=True, blank=True, default=None, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'order'
        verbose_name = '订单'
        verbose_name_plural = '订单'

class Payment(models.Model):
    """
    支付记录表
    字段:
    - order: 关联订单
    - amount: 支付金额(>0)
    - payment_method: 支付方式(微信/支付宝)
    - channel_fee: 渠道手续费
    - status: 支付状态
    """
    PAYMENT_METHOD_CHOICES = (
        ('微信', '微信'),
        ('支付宝', '支付宝')
    )
    STATUS_CHOICES = (
        ('成功', '成功'),
        ('失败', '失败')
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='金额',
        validators=[MinValueValidator(0.01)]
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='支付方式'
    )
    channel_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='手续费'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='支付状态'
    )
    
    class Meta:
        db_table = 'payment'
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'

class AfterSales(models.Model):
    """
    售后工单表
    字段:
    - order: 关联订单
    - type: 售后类型(退款/返工/投诉)
    - status: 工单状态
    """
    TYPE_CHOICES = (
        ('退款', '退款'),
        ('返工', '返工'),
        ('投诉', '投诉')
    )
    STATUS_CHOICES = (
        ('待处理', '待处理'),
        ('已解决', '已解决'),
        ('驳回', '驳回')
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name='售后类型'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='待处理',
        verbose_name='工单状态'
    )
    
    class Meta:
        db_table = 'after_sales'
        verbose_name = '售后工单'
        verbose_name_plural = '售后工单'

class Review(models.Model):
    """
    评价表
    字段:
    - order: 关联订单
    - content: 评价内容
    - status: 审核状态
    """
    STATUS_CHOICES = (
        ('待审核', '待审核'),
        ('通过', '通过'),
        ('驳回', '驳回')
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')
    content = models.TextField(verbose_name='评价内容')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='待审核',
        verbose_name='审核状态'
    )
    
    class Meta:
        db_table = 'review'
        verbose_name = '评价'
        verbose_name_plural = '评价'
