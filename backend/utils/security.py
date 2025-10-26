"""
نظام الأمان والحماية
"""
import hashlib
import secrets
import time
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status


class SecurityUtils:
    """أدوات الأمان"""
    
    @staticmethod
    def generate_activation_code(length: int = 6) -> str:
        """توليد كود التفعيل"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """توليد كلمة مرور عشوائية آمنة"""
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@$!%*?&#'
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # التأكد من احتواء كل أنواع الأحرف
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '@$!%*?&#' for c in password)
        
        if not all([has_lower, has_upper, has_digit, has_special]):
            return SecurityUtils.generate_random_password(length)
        
        return password
    
    @staticmethod
    def hash_string(text: str) -> str:
        """تشفير النص باستخدام SHA-256"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """توليد رمز عشوائي آمن"""
        return secrets.token_urlsafe(length)


class RateLimiter:
    """نظام تحديد معدل الطلبات"""
    
    @staticmethod
    def get_client_ip(request):
        """الحصول على IP العميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def is_rate_limited(identifier: str, max_attempts: int, window_seconds: int) -> bool:
        """التحقق من تجاوز الحد المسموح"""
        cache_key = f'rate_limit:{identifier}'
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            return True
        
        cache.set(cache_key, attempts + 1, window_seconds)
        return False
    
    @staticmethod
    def get_remaining_attempts(identifier: str, max_attempts: int) -> int:
        """الحصول على عدد المحاولات المتبقية"""
        cache_key = f'rate_limit:{identifier}'
        attempts = cache.get(cache_key, 0)
        return max(0, max_attempts - attempts)
    
    @staticmethod
    def clear_limit(identifier: str):
        """مسح قيود المحاولات"""
        cache_key = f'rate_limit:{identifier}'
        cache.delete(cache_key)


def rate_limit(max_attempts: int = 5, window_seconds: int = 300):
    """Decorator لتحديد معدل الطلبات"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            identifier = RateLimiter.get_client_ip(request)
            
            if RateLimiter.is_rate_limited(identifier, max_attempts, window_seconds):
                remaining = RateLimiter.get_remaining_attempts(identifier, max_attempts)
                return JsonResponse({
                    'error': 'تم تجاوز الحد المسموح من المحاولات',
                    'remaining_attempts': remaining,
                    'retry_after': window_seconds
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


class LoginAttemptTracker:
    """تتبع محاولات تسجيل الدخول الفاشلة"""
    
    @staticmethod
    def record_failed_attempt(email: str):
        """تسجيل محاولة فاشلة"""
        cache_key = f'login_attempts:{email}'
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, 3600)  # ساعة واحدة
        
        return attempts + 1
    
    @staticmethod
    def is_account_locked(email: str, max_attempts: int = 5) -> bool:
        """التحقق من قفل الحساب"""
        cache_key = f'login_attempts:{email}'
        attempts = cache.get(cache_key, 0)
        return attempts >= max_attempts
    
    @staticmethod
    def clear_attempts(email: str):
        """مسح محاولات تسجيل الدخول"""
        cache_key = f'login_attempts:{email}'
        cache.delete(cache_key)
    
    @staticmethod
    def get_remaining_attempts(email: str, max_attempts: int = 5) -> int:
        """الحصول على عدد المحاولات المتبقية"""
        cache_key = f'login_attempts:{email}'
        attempts = cache.get(cache_key, 0)
        return max(0, max_attempts - attempts)


class TokenManager:
    """إدارة الرموز المؤقتة"""
    
    @staticmethod
    def store_activation_code(email: str, code: str, expiry_minutes: int = 30):
        """حفظ كود التفعيل"""
        cache_key = f'activation:{email}'
        cache.set(cache_key, code, expiry_minutes * 60)
    
    @staticmethod
    def verify_activation_code(email: str, code: str) -> bool:
        """التحقق من كود التفعيل"""
        cache_key = f'activation:{email}'
        stored_code = cache.get(cache_key)
        
        if not stored_code:
            return False
        
        return stored_code == code
    
    @staticmethod
    def delete_activation_code(email: str):
        """حذف كود التفعيل"""
        cache_key = f'activation:{email}'
        cache.delete(cache_key)
