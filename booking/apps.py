"""
预约应用的Django应用配置
包含应用名称、自动字段类型等基础配置
"""

"""
Django应用配置模块，包含：
1. 应用名称配置
2. 应用初始化设置
3. 信号处理器注册
4. 应用级配置参数
"""

"""
Django应用配置模块，包含：
1. 应用名称配置
2. 应用显示名称
3. 应用初始化逻辑

Django app configuration module, contains:
1. App name configuration
2. App verbose name
3. App initialization logic
"""
"""
Django应用配置模块，包含：
1. 应用名称配置
2. 应用显示名称配置
3. 应用初始化配置
4. 信号处理器注册

Django App configuration module, contains:
1. App name configuration
2. App verbose name configuration
3. App initialization configuration
4. Signal handler registration
"""
"""
Django 应用配置模块
功能:
1. 定义应用名称
2. 配置应用元数据
3. 注册应用信号处理器

主要配置:
- 应用名称: booking
- 应用显示名称: 预约服务
- 应用信号处理器

Django App configuration module
Features:
1. Define app name
2. Configure app metadata
3. Register app signal handlers

Main configurations:
- App name: booking
- App verbose name: Booking Service
- App signal handlers
"""
"""
Django 应用配置模块
功能:
1. 定义应用名称
2. 配置应用元数据
3. 设置应用初始化逻辑

主要配置:
- BookingConfig: 预约应用配置类
  - name: 应用名称
  - verbose_name: 应用显示名称

Django App Configuration Module
Features:
1. Define app name
2. Configure app metadata
3. Setup app initialization logic

Main configurations:
- BookingConfig: Booking app configuration class
  - name: App name
  - verbose_name: App display name
"""
"""
Django 应用配置模块
功能:
1. 定义应用配置类
2. 配置应用元数据
3. 注册应用信号

配置项:
- name: 应用名称
- verbose_name: 应用显示名称
- default_auto_field: 默认主键字段类型

Django App Configuration Module
Features:
1. Define app configuration class
2. Configure app metadata
3. Register app signals

Configurations:
- name: App name
- verbose_name: App display name
- default_auto_field: Default primary key field type
"""
from django.apps import AppConfig


class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'
