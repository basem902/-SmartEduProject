"""
Signature and Security Utilities
"""
import hmac
import hashlib
import time
from django.conf import settings


class SignatureHelper:
    """مساعد التوقيع والأمان"""
    
    @staticmethod
    def sign_data(data):
        """
        توقيع البيانات باستخدام HMAC
        
        Args:
            data (str): البيانات للتوقيع
            
        Returns:
            str: البيانات الموقعة (data|signature)
        """
        secret_key = getattr(settings, 'OTP_SECRET_KEY', settings.SECRET_KEY)
        
        signature = hmac.new(
            secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{data}|{signature}"
    
    @staticmethod
    def verify_signature(signed_data):
        """
        التحقق من توقيع البيانات
        
        Args:
            signed_data (str): البيانات الموقعة
            
        Returns:
            str or None: البيانات إذا كان التوقيع صحيح، None otherwise
        """
        try:
            data, signature = signed_data.rsplit('|', 1)
            secret_key = getattr(settings, 'OTP_SECRET_KEY', settings.SECRET_KEY)
            
            expected_sig = hmac.new(
                secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_sig):
                return data
            
            return None
        except:
            return None
    
    @staticmethod
    def sign_payload_with_expiry(data, expiry_minutes=60):
        """
        توقيع البيانات مع وقت انتهاء
        
        Args:
            data (str): البيانات
            expiry_minutes (int): مدة الصلاحية بالدقائق
            
        Returns:
            str: البيانات الموقعة مع الانتهاء
        """
        exp = int(time.time()) + (expiry_minutes * 60)
        payload = f"{data}|{exp}"
        return SignatureHelper.sign_data(payload)
    
    @staticmethod
    def verify_payload_with_expiry(signed_payload):
        """
        التحقق من البيانات الموقعة مع الانتهاء
        
        Args:
            signed_payload (str): البيانات الموقعة
            
        Returns:
            str or None: البيانات إذا كان التوقيع صحيح ولم ينته، None otherwise
        """
        verified = SignatureHelper.verify_signature(signed_payload)
        if not verified:
            return None
        
        try:
            data, exp = verified.rsplit('|', 1)
            
            if int(exp) < time.time():
                return None  # منتهي
            
            return data
        except:
            return None
    
    @staticmethod
    def get_client_ip(request):
        """
        الحصول على IP الحقيقي للمستخدم
        
        Args:
            request: Django request object
            
        Returns:
            str: عنوان IP
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_agent(request):
        """
        الحصول على User Agent
        
        Args:
            request: Django request object
            
        Returns:
            str: User Agent
        """
        return request.META.get('HTTP_USER_AGENT', '')
