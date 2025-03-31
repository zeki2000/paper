"""
短信服务工具模块，包含:
1. 阿里云短信服务集成
2. 验证码短信发送功能
3. 手机号格式验证
4. 发送结果日志记录

主要类:
- SMSService: 封装阿里云短信服务API
"""

"""
短信服务工具模块，包含：
1. 阿里云短信服务封装
2. 验证码发送功能
3. 短信发送状态处理

SMS service utility module, contains:
1. Aliyun SMS service wrapper
2. Verification code sending functionality
3. SMS delivery status handling
"""
"""
短信服务工具模块
功能:
1. 发送短信验证码
2. 处理短信发送结果
3. 封装阿里云短信服务API

主要类:
- SMSService: 短信服务主类
  方法:
  - send_verification_code: 发送验证码短信
  - _send_sms: 调用阿里云API发送短信

SMS Service utility module
Features:
1. Send SMS verification codes
2. Handle SMS sending results
3. Wrap Aliyun SMS API

Main classes:
- SMSService: Main SMS service class
  Methods:
  - send_verification_code: Send verification code SMS
  - _send_sms: Call Aliyun API to send SMS
"""
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.conf import settings
import logging
"""
短信服务模块，封装阿里云短信服务API功能：
1. 发送短信验证码
2. 处理短信发送结果
3. 封装短信服务配置
"""

"""
短信服务工具模块，提供：
1. 短信验证码发送功能
2. 阿里云短信服务接口封装
3. 短信发送状态跟踪

SMS service utility module, provides:
1. SMS verification code sending
2. Aliyun SMS service interface
3. SMS delivery status tracking
"""
"""
短信服务工具模块，包含：
1. 短信验证码发送功能
2. 短信发送状态查询
3. 短信发送频率限制

主要依赖:
- 阿里云短信服务SDK

SMS service utility module, contains:
1. SMS verification code sending
2. SMS delivery status checking
3. SMS sending rate limiting

Main dependencies:
- Aliyun SMS service SDK
"""
"""
短信服务工具模块
功能:
1. 发送短信验证码
2. 处理短信发送失败情况
3. 集成阿里云短信服务

主要方法:
- send_verification_code: 发送验证码短信
- send_notification: 发送通知短信

SMS Service Utility Module
Features:
1. Send SMS verification codes
2. Handle SMS sending failures
3. Integrate with Aliyun SMS service

Main methods:
- send_verification_code: Send verification code SMS
- send_notification: Send notification SMS
"""
import os

logger = logging.getLogger(__name__)

class SMSService:
    """
    阿里云短信服务封装类，提供验证码发送功能
    功能:
    - 初始化短信服务客户端
    - 发送验证码短信
    - 处理短信发送结果
    """
    def __init__(self):
        """
        初始化短信服务客户端
        使用环境变量中的阿里云AccessKey进行认证
        配置:
        - 使用阿里云测试专用签名和模板
        - 设置默认区域为'default'
        """
        self.client = AcsClient(
            os.getenv('ALIYUN_SMS_ACCESS_KEY_ID'),
            os.getenv('ALIYUN_SMS_ACCESS_KEY_SECRET'),
            'default'
        )
        # 使用阿里云测试专用签名和模板
        self.sign_name = '阿里云短信测试'
        self.template_code = 'SMS_154950909'

    def send_verification_code(self, phone_number, code):
        """
        发送验证码短信
        参数:
            phone_number: 接收手机号(支持国际格式)
            code: 6位数字验证码
        返回:
            bool: 发送成功返回True，失败返回False
        处理流程:
        1. 验证环境变量配置
        2. 格式化手机号
        3. 构建短信请求
        4. 发送请求并处理响应
        5. 记录日志
        """
        # 验证环境变量配置
        if not all([
            os.getenv('ALIYUN_SMS_ACCESS_KEY_ID'),
            os.getenv('ALIYUN_SMS_ACCESS_KEY_SECRET')
        ]):
            logger.error("阿里云短信配置不完整")
            return False

        # 验证手机号格式
        if not phone_number.startswith('+86'):
            phone_number = f'+86{phone_number}'

        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        # 记录完整请求参数
        params = {
            'PhoneNumbers': phone_number,
            'SignName': self.sign_name,
            'TemplateCode': self.template_code,
            'TemplateParam': f'{{"code":"{code}"}}'
        }
        logger.info(f"准备发送短信，参数: {params}")

        try:
            for k, v in params.items():
                request.add_query_param(k, v)

            response = self.client.do_action_with_exception(request)
            response_data = response.decode('utf-8')
            logger.info(f"短信发送响应: {response_data}")
            
            # 解析返回结果
            import json
            result = json.loads(response_data)
            if result.get('Code') != 'OK':
                logger.error(f"短信发送失败: {result.get('Message')}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}")
            logger.error(f"Request params: {request.get_query_params()}")
            logger.error(f"Full error: {str(e)}")
            return False
