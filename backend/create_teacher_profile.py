"""
إنشاء سجل معلم لحساب موجود
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import Teacher

username = 'basem2025'

try:
    # البحث عن المستخدم
    user = User.objects.get(username=username)
    print(f"✅ المستخدم موجود: {user.username}")
    
    # التحقق من وجود سجل معلم
    teacher, created = Teacher.objects.get_or_create(
        user=user,
        defaults={
            'full_name': user.username,
            'email': user.email,
            'phone': '0500000000',
            'school_name': 'مدرسة تجريبية',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ تم إنشاء سجل معلم جديد")
        print(f"   الاسم: {teacher.full_name}")
        print(f"   البريد: {teacher.email}")
    else:
        print(f"✅ سجل المعلم موجود مسبقاً")
        print(f"   الاسم: {teacher.full_name}")
        print(f"   البريد: {teacher.email}")
        print(f"   نشط: {teacher.is_active}")
    
    print("\n" + "="*50)
    print("يمكنك الآن تسجيل الدخول والوصول للوحة التحكم")
    print("="*50)
    
except User.DoesNotExist:
    print(f"❌ المستخدم {username} غير موجود!")
except Exception as e:
    print(f"❌ خطأ: {e}")
