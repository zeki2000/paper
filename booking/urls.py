"""
URL路由配置模块，包含：
1. 用户认证相关路由：
   - 登录/注册
   - 密码重置
   - 验证码发送
   - 用户登出
2. 服务相关路由：
   - 首页
   - 服务分类列表
   - 订单创建
3. 政策条款路由：
   - 服务条款
   - 隐私政策
4. 门户路由：
   - 用户门户
   - 服务商门户
"""

"""
URL路由配置模块，定义所有URL路径与视图的映射关系：
1. 用户认证相关路由：
   - 登录/注册
   - 密码重置
   - 验证码发送
   - 用户登出
2. 服务相关路由：
   - 首页
   - 服务列表
   - 订单创建
3. 政策条款路由：
   - 服务条款
   - 隐私政策
4. 门户路由：
   - 用户门户
   - 服务商门户
"""

"""
URL路由配置模块，定义：
1. 所有前端页面的URL路径
2. API接口端点
3. 视图函数映射关系

URL routing configuration module, defines:
1. All frontend page URLs
2. API endpoints
3. View function mappings
"""
"""
URL路由配置模块，包含：
1. 用户认证相关路由(登录/注册/密码重置)
2. 服务相关路由(首页/服务列表/订单创建)
3. 门户路由(用户门户/服务商门户)
4. 政策条款路由(服务条款/隐私政策)

URL routing configuration module, contains:
1. Authentication routes (login/register/password reset)
2. Service related routes (home/service list/order creation)
3. Portal routes (user portal/service provider portal)
4. Policy routes (terms of service/privacy policy)
"""
"""
URL路由配置模块，包含：
1. 用户认证相关路由(登录/注册/密码重置)
2. 服务相关路由(首页/服务列表/订单创建)
3. 门户路由(用户门户/服务商门户)
4. 政策条款路由(服务条款/隐私政策)

URL routing configuration module, contains:
1. Authentication routes (login/register/password reset)
2. Service related routes (home/service list/order creation)
3. Portal routes (user portal/service provider portal)
4. Policy routes (terms of service/privacy policy)
"""
"""
URL路由配置模块，定义:
1. 用户认证相关URL
2. 服务相关URL
3. 门户页面URL
4. 政策条款URL

URL patterns configuration module, defines:
1. Authentication related URLs
2. Service related URLs
3. Portal page URLs
4. Policy page URLs
"""
"""
URL 路由配置模块
功能:
1. 定义应用的所有URL模式
2. 将URL映射到视图函数
3. 配置URL命名空间

主要路由:
- 用户认证路由(登录/注册/密码重置)
- 服务相关路由(首页/服务列表/订单创建)
- 门户路由(用户门户/服务商门户)
- 政策条款路由(服务条款/隐私政策)

URL Routing configuration module
Features:
1. Define all URL patterns for the app
2. Map URLs to view functions
3. Configure URL namespaces

Main routes:
- Authentication routes (login/register/password reset)
- Service related routes (home/service list/order creation)
- Portal routes (user portal/service provider portal)
- Policy routes (terms of service/privacy policy)
"""
"""
URL 路由配置模块
功能:
1. 定义应用的所有URL模式
2. 将URL映射到视图函数
3. 配置URL命名空间

主要路由:
- 用户认证路由(登录/注册/登出)
- 服务相关路由(首页/服务列表/订单)
- 门户路由(用户门户/服务商门户)
- 政策条款路由(服务条款/隐私政策)

URL Routing Configuration Module
Features:
1. Define all URL patterns for the app
2. Map URLs to view functions
3. Configure URL namespaces

Main routes:
- Authentication routes (login/register/logout)
- Service related routes (home/service list/orders)
- Portal routes (user portal/service provider portal)
- Policy routes (terms of service/privacy policy)
"""
"""
URL路由配置模块
功能:
1. 定义应用URL路由
2. 配置视图映射
3. 设置URL命名空间

主要路由:
- /: 首页路由
- /api/: API接口路由
- /auth/: 认证相关路由
- /booking/: 预约相关路由

URL Routing Configuration Module
Features:
1. Define app URL routes
2. Configure view mappings
3. Setup URL namespaces

Main routes:
- /: Home page route
- /api/: API interface routes
- /auth/: Authentication related routes
- /booking/: Booking related routes
"""
"""
URL路由配置模块
功能:
1. 定义URL到视图的映射
2. 组织URL命名空间
3. 配置URL参数

主要路由:
- 用户认证路由(登录/注册/密码重置)
- 服务相关路由(首页/服务列表/订单创建)
- 门户路由(用户门户/服务商门户)
- 政策条款路由(服务条款/隐私政策)

URL Routing Configuration Module
Features:
1. Define URL to view mappings
2. Organize URL namespaces
3. Configure URL parameters

Main routes:
- Authentication routes (login/register/password reset)
- Service related routes (home/service list/order creation)
- Portal routes (user portal/service provider portal)
- Policy routes (terms of service/privacy policy)
"""
from django.urls import path
from . import views

urlpatterns = [
    # 用户认证相关路由
    path('accounts/login/', views.auth_view, name='login'),  # 处理用户登录/注册请求
    path('password_reset/', views.password_reset, name='password_reset'),  # 处理密码重置请求
    path('logout/', views.user_logout, name='logout'),  # 处理用户登出请求
    path('send_code/', views.send_verification_code, name='send_code'),  # 处理验证码发送请求
    
    # 服务相关路由
    path('', views.home, name='home'),  # 显示首页服务列表
    path('category/<int:category_id>/', views.service_list, name='service_list'),  # 显示指定分类的服务列表
    path('service/<int:service_id>/order/', views.create_order, name='create_order'),  # 处理订单创建请求
    
    # 政策条款路由
    path('terms/', views.terms_view, name='terms'),  # 显示服务条款页面
    path('privacy/', views.privacy_view, name='privacy'),  # 显示隐私政策页面
    
    # 门户路由
    path('portal/', views.service_portal, name='service_portal'),  # 显示服务商门户页面
    path('user_portal/', views.user_portal, name='user_portal'),  # 显示用户门户页面
]
