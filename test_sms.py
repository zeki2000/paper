import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_service_booking.settings')
django.setup()

from booking.utils.sms_service import SMSService
import logging

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_send_sms(phone_number):
    sms = SMSService()
    print(f"尝试向 {phone_number} 发送测试短信...")
    success = sms.send_verification_code(phone_number, "123456")
    if success:
        print("短信发送成功")
    else:
        print("短信发送失败，请检查日志获取详细信息")

if __name__ == "__main__":
    # 请替换为您的测试手机号（带国际区号）
    test_phone = "+8615173291587"  
    test_send_sms(test_phone)
