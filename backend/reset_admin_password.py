"""
إعادة تعيين كلمة مرور المدير
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

username = 'basem902'
new_password = 'admin123'  # كلمة المرور الجديدة

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()
    
    print(f"✅ تم إعادة تعيين كلمة المرور لـ {username}")
    print(f"\nمعلومات تسجيل الدخول:")
    print(f"Username: {username}")
    print(f"Password: {new_password}")
    print(f"\n⚠️ غيّر كلمة المرور بعد تسجيل الدخول!")
    
except User.DoesNotExist:
    print(f"❌ المستخدم {username} غير موجود!")
    print("شغّل السكريبت check_admin.py أولاً")
