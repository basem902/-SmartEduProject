"""
OTP System App Configuration
"""
from django.apps import AppConfig


class OtpSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.otp_system'
    verbose_name = 'نظام رموز التحقق OTP'
