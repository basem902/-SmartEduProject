"""
سكريبت للتحقق من حساب المدير
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

# البحث عن المستخدم
username = 'basem902'
try:
    user = User.objects.get(username=username)
    print(f"✅ المستخدم موجود: {user.username}")
    print(f"   - Email: {user.email}")
    print(f"   - Is superuser: {user.is_superuser}")
    print(f"   - Is staff: {user.is_staff}")
    print(f"   - Is active: {user.is_active}")
    
    if user.is_superuser:
        print("\n✅ الحساب له صلاحيات superuser")
    else:
        print("\n❌ الحساب ليس superuser!")
        print("تشغيل الأمر لتحويله إلى superuser...")
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("✅ تم تحويل الحساب إلى superuser")
        
except User.DoesNotExist:
    print(f"❌ المستخدم {username} غير موجود!")
    print("\nإنشاء حساب superuser جديد...")
    
    # إنشاء superuser
    user = User.objects.create_superuser(
        username='basem902',
        email='basem902@gmail.com',
        password='admin123'  # غيّر هذه الكلمة!
    )
    print(f"✅ تم إنشاء superuser: {user.username}")
    print(f"   كلمة المرور: admin123")
    print("\n⚠️ تذكر تغيير كلمة المرور!")

print("\n" + "="*50)
print("يمكنك الآن تسجيل الدخول:")
print(f"Username: {username}")
print("="*50)
