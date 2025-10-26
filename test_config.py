"""
اختبار سريع للإعدادات
"""
import os
import sys
from pathlib import Path

# إضافة مسار Backend
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# تحميل Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    import django
    django.setup()
    from django.conf import settings
    
    print("=" * 60)
    print("✅ Django Settings - تم التحميل بنجاح")
    print("=" * 60)
    
    # التحقق من الإعدادات الأساسية
    print("\n📌 الإعدادات الأساسية:")
    print(f"  DEBUG: {settings.DEBUG}")
    print(f"  SECRET_KEY: {settings.SECRET_KEY[:20]}...")
    print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # Database
    print("\n📌 قاعدة البيانات:")
    db_name = settings.DATABASES['default']['NAME']
    print(f"  Database: {db_name[:30]}...")
    
    # Email
    print("\n📌 البريد الإلكتروني:")
    print(f"  SMTP Email: {settings.EMAIL_HOST_USER}")
    print(f"  SMTP Host: {settings.EMAIL_HOST}")
    
    # Gemini
    print("\n📌 الذكاء الاصطناعي:")
    if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
        print(f"  GEMINI API Key: {settings.GEMINI_API_KEY[:20]}...")
    else:
        print("  ⚠️  GEMINI_API_KEY غير موجود")
    
    # Telegram Bot
    print("\n📌 Telegram Bot:")
    if hasattr(settings, 'TELEGRAM_BOT_TOKEN') and settings.TELEGRAM_BOT_TOKEN:
        print(f"  ✅ Bot Token: {settings.TELEGRAM_BOT_TOKEN[:20]}...")
        print(f"  ✅ Bot Username: @{settings.TELEGRAM_BOT_USERNAME}")
        print(f"  ✅ OTP Secret: {settings.OTP_SECRET_KEY[:20]}...")
        print(f"  ✅ Frontend URL: {settings.FRONTEND_URL}")
    else:
        print("  ⚠️  إعدادات Telegram Bot غير موجودة")
    
    # CORS
    print("\n📌 CORS:")
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        print(f"  Allowed Origins: {len(settings.CORS_ALLOWED_ORIGINS)} origins")
    
    print("\n" + "=" * 60)
    print("✅ جميع الإعدادات تم تحميلها بنجاح!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ خطأ: {e}")
    import traceback
    traceback.print_exc()
