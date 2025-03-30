import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
import random
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from .models import User, Service, ServiceCategory, Order, VerificationCode

# 阿里云短信配置
ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_SMS_ACCESS_KEY_ID')
ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_SMS_ACCESS_KEY_SECRET') 
ALIYUN_SIGN_NAME = os.getenv('ALIYUN_SMS_SIGN_NAME')
ALIYUN_TEMPLATE_CODE = os.getenv('ALIYUN_SMS_TEMPLATE_CODE')

def terms_view(request):
    return render(request, 'booking/terms.html')

def privacy_view(request):
    return render(request, 'booking/privacy.html')

def send_verification_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            
            if not phone:
                return JsonResponse({'success': False, 'message': '手机号不能为空'}, status=400)
            
            # 频率限制：60秒内只能发送一次
            last_code = VerificationCode.objects.filter(
                phone=phone,
                created_at__gte=timezone.now()-timedelta(seconds=60))
            if last_code.exists():
                return JsonResponse(
                    {'success': False, 'message': '操作过于频繁，请稍后再试'},
                    status=429)
            
            # 生成并保存验证码
            code = VerificationCode.generate_code(phone)
            
            # 调用短信服务发送验证码
            from .utils.sms_service import SMSService
            sms_service = SMSService()
            if sms_service.send_verification_code(phone, code):
                return JsonResponse({
                    'success': True, 
                    'message': '验证码已发送'
                }, status=200)
            return JsonResponse({
                'success': False,
                'message': '短信发送失败，请稍后重试'
            }, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '无效请求'})

def auth_view(request):
    # 手机号检查API
    if request.method == 'GET' and 'check_phone' in request.GET:
        phone = request.GET.get('check_phone')
        if not phone or len(phone) != 11 or not phone.isdigit():
            return JsonResponse(
                {'exists': False, 'error': '无效的手机号格式'},
                status=400)
        
        exists = User.objects.filter(phone=phone).exists()
        return JsonResponse({'exists': exists}, status=200)
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        code = request.POST.get('code', None)
        login_type = request.POST.get('login_type')
        
        # 输入验证
        if not phone or len(phone) != 11 or not phone.isdigit():
            messages.error(request, '请输入有效的手机号')
            return render(request, 'booking/login.html', status=400)
        
        # 密码登录逻辑
        if login_type == 'password':
            if not password or len(password) < 6:
                messages.error(request, '密码长度不能少于6位')
                return render(request, 'booking/login.html', status=400)
            
            user = authenticate(request, username=phone, password=password)
            if user:
                login(request, user)
                return redirect('home')
            messages.error(request, '手机号或密码错误')
            return render(request, 'booking/login.html', status=401)
        
        # 验证码登录/注册逻辑
        if login_type != 'code':
            messages.error(request, '无效的登录类型')
            return render(request, 'booking/login.html', status=400)
            
        verification = VerificationCode.objects.filter(
            phone=phone,
            code=code,
            created_at__gte=timezone.now()-timedelta(minutes=5))
        
        if not verification.exists():
            messages.error(request, '验证码错误或已过期')
            return render(request, 'booking/login.html', status=400)
        
        try:
            # 随机用户名和默认头像
            username = f'user_{phone[-4:]}'
            avatar = f'avatars/default_{random.randint(1,5)}.png'
            
            user = User.objects.create_user(
                phone=phone,
                username=username,
                password=password,
                avatar=avatar
            )
            login(request, user)
            return redirect('home')
        except Exception as e:
            messages.error(request, f'注册失败: {str(e)}')
    
    return render(request, 'booking/login.html')

def password_reset(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        
        # 验证验证码
        verification = VerificationCode.objects.filter(
            phone=phone,
            code=code,
            created_at__gte=timezone.now()-timedelta(minutes=5)
        ).first()
        
        if not verification:
            messages.error(request, '验证码错误或已过期')
            return render(request, 'booking/password_reset.html')
        
        try:
            user = User.objects.get(phone=phone)
            user.set_password(new_password)
            user.save()
            messages.success(request, '密码重置成功，请重新登录')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, '用户不存在')
    
    return render(request, 'booking/password_reset.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

def home(request):
    categories = ServiceCategory.objects.all()
    services = Service.objects.all()
    return render(request, 'booking/home.html', {
        'categories': categories,
        'services': services
    })

@login_required
def service_list(request, category_id):
    category = ServiceCategory.objects.get(id=category_id)
    services = Service.objects.filter(category=category)
    return render(request, 'booking/service_list.html', {
        'category': category,
        'services': services
    })

@login_required
def create_order(request, service_id):
    service = Service.objects.get(id=service_id)
    if request.method == 'POST':
        # Process order creation
        pass
    return render(request, 'booking/create_order.html', {
        'service': service
    })
