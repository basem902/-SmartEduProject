"""
FastAPI Telegram Client
للاتصال بـ FastAPI Telegram Service من Django
"""
import requests
from django.conf import settings
from typing import Dict, Any


class TelegramFastAPIClient:
    """عميل للاتصال بخدمة FastAPI"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'TELEGRAM_FASTAPI_URL', 'http://localhost:8001')
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """إرسال طلب POST"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=data,
                timeout=30
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'فشل الاتصال بخدمة Telegram: {str(e)}'
            }
    
    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """إرسال طلب GET"""
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=30
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'فشل الاتصال بخدمة Telegram: {str(e)}'
            }
    
    def _delete(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """إرسال طلب DELETE"""
        try:
            response = requests.delete(
                f"{self.base_url}{endpoint}",
                json=data,
                timeout=30
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'فشل الاتصال بخدمة Telegram: {str(e)}'
            }
    
    def send_code(self, phone_number: str) -> Dict[str, Any]:
        """إرسال كود التحقق"""
        return self._post('/telegram/send-code', {'phone_number': phone_number})
    
    def resend_code(self, phone_number: str) -> Dict[str, Any]:
        """إعادة إرسال الكود"""
        return self._post('/telegram/resend-code', {'phone_number': phone_number})
    
    def verify_code(self, phone_number: str, code: str, phone_code_hash: str) -> Dict[str, Any]:
        """التحقق من الكود"""
        return self._post('/telegram/verify-code', {
            'phone_number': phone_number,
            'code': code,
            'phone_code_hash': phone_code_hash
        })
    
    def verify_password(self, phone_number: str, password: str) -> Dict[str, Any]:
        """التحقق من كلمة مرور 2FA"""
        return self._post('/telegram/verify-password', {
            'phone_number': phone_number,
            'password': password
        })
    
    def get_session_status(self, phone_number: str) -> Dict[str, Any]:
        """الحصول على حالة الجلسة"""
        return self._get('/telegram/session-status', {'phone_number': phone_number})
    
    def delete_session(self, phone_number: str) -> Dict[str, Any]:
        """حذف الجلسة"""
        return self._delete('/telegram/delete-session', {'phone_number': phone_number})
    
    def health_check(self) -> Dict[str, Any]:
        """فحص صحة الخدمة"""
        return self._get('/health')


# Singleton
telegram_fastapi_client = TelegramFastAPIClient()
