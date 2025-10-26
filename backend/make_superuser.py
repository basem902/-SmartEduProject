"""
تحويل مستخدم عادي إلى superuser
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

username = 'basem2025'

try:
    user = User.objects.get(username=username)
    
    if user.is_superuser:
        print(f"✅ {username} هو بالفعل superuser")
    else:
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"✅ تم تحويل {username} إلى superuser")
        
    print(f"\nيمكنك الآن تسجيل الدخول:")
    print(f"Username: {username}")
    print(f"URL: http://localhost:5500/admin/")
    
except User.DoesNotExist:
    print(f"❌ المستخدم {username} غير موجود!")
    print("تأكد من اسم المستخدم أو أنشئ حساب جديد")
