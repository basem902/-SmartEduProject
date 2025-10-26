#!/usr/bin/env python
"""
فحص وإنشاء حساب superuser
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("👤 فحص حسابات Superuser")
print("=" * 60)

# فحص جميع المستخدمين
all_users = User.objects.all()
superusers = User.objects.filter(is_superuser=True)
staff_users = User.objects.filter(is_staff=True)

print(f"\n📊 الإحصائيات:")
print(f"   - جميع المستخدمين: {all_users.count()}")
print(f"   - Superusers: {superusers.count()}")
print(f"   - Staff: {staff_users.count()}")

print(f"\n👥 جميع المستخدمين:")
for user in all_users:
    superuser_icon = "⭐" if user.is_superuser else "👤"
    staff_icon = "🔑" if user.is_staff else ""
    print(f"   {superuser_icon} {staff_icon} {user.username} ({user.email})")
    print(f"      - Superuser: {user.is_superuser}")
    print(f"      - Staff: {user.is_staff}")
    print(f"      - Active: {user.is_active}")

# البحث عن basem902
basem_user = User.objects.filter(username='basem902').first()

print("\n" + "=" * 60)
if basem_user:
    print("✅ حساب basem902 موجود!")
    print(f"   - ID: {basem_user.id}")
    print(f"   - Email: {basem_user.email}")
    print(f"   - Superuser: {basem_user.is_superuser}")
    print(f"   - Staff: {basem_user.is_staff}")
    print(f"   - Active: {basem_user.is_active}")
    
    if not basem_user.is_superuser:
        print("\n⚠️ الحساب موجود لكن ليس Superuser!")
        print("   → سأقوم بترقيته...")
        
        basem_user.is_superuser = True
        basem_user.is_staff = True
        basem_user.save()
        
        print("✅ تم الترقية إلى Superuser!")
else:
    print("❌ حساب basem902 غير موجود!")
    print("\n📝 سأقوم بإنشائه الآن...")
    
    # إنشاء حساب جديد
    basem_user = User.objects.create_superuser(
        username='basem902',
        email='basem902@gmail.com',
        password='Zxcvb123asd@'
    )
    
    print("✅ تم إنشاء Superuser بنجاح!")
    print(f"   - Username: basem902")
    print(f"   - Email: basem902@gmail.com")
    print(f"   - Password: Zxcvb123asd@")
    print(f"   - ID: {basem_user.id}")

print("\n" + "=" * 60)
print("🎉 اكتمل الفحص!")
print("=" * 60)

# التحقق النهائي
final_superusers = User.objects.filter(is_superuser=True)
print(f"\n✅ عدد Superusers الآن: {final_superusers.count()}")
for su in final_superusers:
    print(f"   ⭐ {su.username} ({su.email})")

print("\n🚀 يمكنك الآن تسجيل الدخول:")
print("   - Username: basem902")
print("   - Password: Zxcvb123asd@")
print("   - رابط Admin Panel: http://localhost:5500/admin/")
