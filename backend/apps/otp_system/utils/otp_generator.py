"""
OTP Generation Utilities
"""
import secrets
from datetime import timedelta
from django.utils import timezone


class OTPGenerator:
    """مولد رموز OTP"""
    
    @staticmethod
    def generate_code(length=6):
        """
        توليد كود مكون من أرقام
        
        Args:
            length (int): طول الكود (افتراضي 6)
            
        Returns:
            str: الكود المولد
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    def generate_submit_token():
        """
        توليد رمز تسليم آمن
        
        Returns:
            str: رمز التسليم
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def calculate_expiry(minutes=10):
        """
        حساب وقت انتهاء الصلاحية
        
        Args:
            minutes (int): عدد الدقائق (افتراضي 10)
            
        Returns:
            datetime: وقت الانتهاء
        """
        return timezone.now() + timedelta(minutes=minutes)
    
    @staticmethod
    def is_code_valid(code):
        """
        التحقق من صحة تنسيق الكود
        
        Args:
            code (str): الكود للتحقق
            
        Returns:
            bool: True إذا كان الكود صحيح
        """
        if not code:
            return False
        
        if len(code) != 6:
            return False
        
        if not code.isdigit():
            return False
        
        return True
