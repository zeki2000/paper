from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.client = AcsClient(
            settings.ALIYUN_SMS_ACCESS_KEY_ID,
            settings.ALIYUN_SMS_ACCESS_KEY_SECRET,
            'default'
        )

    def send_verification_code(self, phone_number, code):
        """发送验证码短信"""
        # 验证环境变量配置
        if not all([
            settings.ALIYUN_SMS_ACCESS_KEY_ID,
            settings.ALIYUN_SMS_ACCESS_KEY_SECRET,
            settings.ALIYUN_SMS_SIGN_NAME,
            settings.ALIYUN_SMS_TEMPLATE_CODE
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
            'SignName': settings.ALIYUN_SMS_SIGN_NAME,
            'TemplateCode': settings.ALIYUN_SMS_TEMPLATE_CODE,
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
            logger.error(f"Error details: {e.__dict__}")
            return False
