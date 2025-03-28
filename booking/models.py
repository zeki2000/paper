from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import random
from datetime import timedelta
from django.utils import timezone

class VerificationCode(models.Model):
    phone = models.CharField(max_length=11)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'verification_code'
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        
    @classmethod
    def generate_code(cls, phone):
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
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^1[3-9]\d{9}$',
                message='请输入正确的手机号码'
            )
        ]
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_service_provider = models.BooleanField(default=False)
    rating = models.FloatField(default=5.0)
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

class ServiceCategory(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'service_category'
        verbose_name = '服务类别'
        verbose_name_plural = '服务类别'

class Service(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # in minutes
    
    class Meta:
        db_table = 'service'
        verbose_name = '服务项目'
        verbose_name_plural = '服务项目'

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provided_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_time = models.DateTimeField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order'
        verbose_name = '订单'
        verbose_name_plural = '订单'
