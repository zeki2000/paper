"""
视图函数模块
功能:
1. 处理HTTP请求
2. 实现业务逻辑
3. 返回响应

主要视图:
- 用户认证视图(登录/注册/密码重置)
- 服务相关视图(首页/服务列表/订单创建)
- 门户视图(用户门户/服务商门户)
- 政策条款视图(服务条款/隐私政策)
"""

import os
"""
视图模块，包含：
1. 用户认证视图(登录/注册/登出)
2. 服务相关视图(首页/服务列表/订单创建)
3. 门户视图(用户门户/服务商门户)
4. 政策条款视图(服务条款/隐私政策)
"""
"""
视图模块，包含:
1. 用户认证视图(登录/注册/密码重置)
2. 服务相关视图(首页/服务列表/订单创建)
3. 门户视图(用户门户/服务商门户)
4. 政策条款视图(服务条款/隐私政策)

主要功能:
- 处理HTTP请求
- 调用业务逻辑
- 返回响应(HTML/JSON)
"""
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
    """
    显示服务条款页面
    参数:
        request: HTTP请求对象
    返回:
        渲染的服务条款页面
    """
    return render(request, 'booking/terms.html')

def privacy_view(request):
    """
    显示隐私政策页面
    参数:
        request: HTTP请求对象
    返回:
        渲染的隐私政策页面
    """
    return render(request, 'booking/privacy.html')

def send_verification_code(request):
    """
    发送短信验证码
    参数:
        request: 包含手机号的POST请求
    返回:
        JsonResponse: 包含发送结果的JSON响应
    """
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
    """
    用户认证视图，处理登录/注册请求
    支持两种认证方式:
    1. 密码登录(已注册用户)
    2. 验证码登录(新用户自动注册)
    参数:
        request: 包含认证信息的请求
    返回:
        成功: 重定向到用户门户或服务商门户
        失败: 返回登录页面并显示错误信息
    """
    """
    处理用户认证(登录/注册)
    支持密码登录和验证码登录两种方式
    参数:
        request: 包含认证信息的请求
    返回:
        成功: 重定向到用户门户或服务商门户
        失败: 返回登录页面并显示错误信息
    """
    import logging
    logger = logging.getLogger(__name__)
    
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
            logger.debug(f"Password login attempt for phone: {phone}")
            if not password or len(password) < 6:
                messages.error(request, '密码长度不能少于6位')
                return render(request, 'booking/login.html', status=400)
            
            user = authenticate(request, username=phone, password=password)
            if user:
                logger.debug(f"User authenticated successfully: {user}")
                login(request, user)
                return redirect('user_portal')
            logger.debug(f"Authentication failed for phone: {phone}")
            messages.error(request, '手机号或密码错误')
            return render(request, 'booking/login.html', status=401)
        
        # 验证码登录/注册逻辑
        if login_type != 'code':
            return JsonResponse({'success': False, 'message': '无效的登录类型'}, status=400)
            
        # 验证验证码是否正确
        verification = VerificationCode.objects.filter(
            phone=phone,
            code=code,
            created_at__gte=timezone.now()-timedelta(minutes=5))
        
        if not verification.exists():
            return JsonResponse({'success': False, 'message': '验证码错误或已过期'}, status=400)
        
        verification = verification.first()
        
        try:
            # 检查用户是否已存在
            user = User.objects.filter(phone=phone).first()
            
            if not user:
                # 新用户注册
                username = f'user_{phone[-4:]}'
                avatar = f'avatars/default_{random.randint(1,5)}.png'
                
                # 生成随机密码
                password = User.objects.make_random_password()
                
                # 创建用户
                user = User.objects.create_user(
                    phone=phone,
                    username=username,
                    password=password,
                    role='C'  # 默认为普通用户
                )
                
                # 创建用户信息(包含avatar)
                from .models import UserInfo
                UserInfo.objects.create(
                    user=user,
                    nickname=username,
                    avatar=avatar
                )
            
            # 登录用户
            login(request, user)
            
            # 更新验证码使用状态
            verification.is_used = True
            verification.save()
            
            # 返回JSON响应
            return JsonResponse({
                'success': True,
                'message': '验证成功',
                'redirect_url': 'service_portal' if user.role == 'B' else 'user_portal'
            })
        except Exception as e:
            logger.error(f'验证码登录失败: {str(e)}')
            return JsonResponse({
                'success': False,
                'message': f'登录失败: {str(e)}'
            }, status=500)
    
    # 非AJAX请求返回登录页面
    return render(request, 'booking/login.html')

def password_reset(request):
    """
    密码重置视图
    参数:
        request: 包含手机号、验证码和新密码的POST请求
    返回:
        成功: 重定向到登录页面
        失败: 返回密码重置页面并显示错误
    """
    """
    处理密码重置请求
    参数:
        request: 包含手机号、验证码和新密码的POST请求
    返回:
        成功: 重定向到登录页面
        失败: 返回密码重置页面并显示错误
    """
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
    """处理用户登出请求"""
    logout(request)
    return redirect('home')

@login_required
def user_portal(request):
    """
    显示用户门户页面
    参数:
        request: HTTP请求对象
    返回:
        渲染的用户门户页面，包含:
        - 服务类别列表
        - 服务项目列表
        - 用户信息
    """
    categories = ServiceCategory.objects.all()
    services = Service.objects.all()
    user_info = request.user.userinfo  # 获取关联的UserInfo
    return render(request, 'booking/user_portal.html', {
        'categories': categories,
        'services': services,
        'user_info': user_info
    })

@login_required
def service_portal(request):
    """
    显示服务商门户页面
    参数:
        request: HTTP请求对象
    返回:
        渲染的服务商门户页面，包含:
        - 服务类别列表
        - 服务项目列表
    """
    """显示服务提供商门户页面"""
    categories = ServiceCategory.objects.all()
    services = Service.objects.all()
    return render(request, 'booking/service_portal.html', {
        'categories': categories,
        'services': services
    })

def home(request):
    """
    显示首页
    参数:
        request: HTTP请求对象
    返回:
        渲染的首页，包含:
        - 所有服务类别
        - 热门服务项目
    """
    """显示首页"""
    categories = ServiceCategory.objects.all()
    services = Service.objects.all()
    return render(request, 'booking/home.html', {
        'categories': categories,
        'services': services
    })

@login_required
def service_list(request, category_id):
    """
    显示指定类别的服务列表
    参数:
        request: HTTP请求对象
        category_id: 服务类别ID
    返回:
        渲染的服务列表页面，包含:
        - 当前服务类别信息
        - 该类别下的所有服务项目
    """
    """
    显示指定类别的服务列表
    参数:
        category_id: 服务类别ID
    返回:
        渲染的服务列表页面
    """
    category = ServiceCategory.objects.get(id=category_id)
    services = Service.objects.filter(category=category)
    return render(request, 'booking/service_list.html', {
        'category': category,
        'services': services
    })

@login_required
def create_order(request, service_id):
    """
    处理订单创建请求
    参数:
        request: HTTP请求对象
        service_id: 服务ID
    返回:
        GET请求: 渲染订单创建页面
        POST请求: 处理订单创建逻辑
    """
    """
    处理订单创建请求
    参数:
        service_id: 服务ID
    返回:
        订单创建页面
    """
    service = Service.objects.get(id=service_id)
    if request.method == 'POST':
        # Process order creation
        pass
    return render(request, 'booking/create_order.html', {
        'service': service
    })
