#!/usr/bin/env python
"""
إنشاء Teacher record للمستخدم basem902@gmail.com
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import Teacher
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 50)
print("🔧 إصلاح Teacher record")
print("=" * 50)

# الحصول على User
user = User.objects.get(email='basem902@gmail.com')
print(f"\n✅ User موجود: {user.email} (id={user.id})")

# التحقق من وجود Teacher
teacher = Teacher.objects.filter(email=user.email).first()

if teacher:
    print(f"⚠️ Teacher موجود مسبقاً: {teacher.email} (id={teacher.id})")
    
    if not teacher.user:
        print(f"🔗 ربط Teacher بـ User...")
        teacher.user = user
        teacher.save()
        print(f"✅ تم الربط بنجاح!")
    else:
        print(f"✅ Teacher مربوط بالفعل")
else:
    print(f"\n📝 إنشاء Teacher record جديد...")
    
    # إنشاء Teacher
    teacher = Teacher.objects.create(
        user=user,
        email=user.email,
        full_name="باسم",  # يمكن تعديله لاحقاً
        phone="0558048004",  # رقم بدون +966 (10 أحرف)
        school_name="مدرسة الثانوية",
        is_active=True,
        password_hash="temporary"  # مؤقت
    )
    
    print(f"✅ تم إنشاء Teacher (id={teacher.id})")

print("\n" + "=" * 50)
print("🎉 الإصلاح مكتمل!")
print("=" * 50)

# التحقق النهائي
user_fresh = User.objects.get(id=user.id)
if hasattr(user_fresh, 'teacher_profile'):
    print(f"✅ User.teacher_profile موجود: {user_fresh.teacher_profile}")
else:
    print(f"❌ User.teacher_profile غير موجود!")

teacher_fresh = Teacher.objects.get(email=user.email)
print(f"✅ Teacher موجود: {teacher_fresh}")
print(f"✅ Teacher.user = {teacher_fresh.user}")

print("\n🚀 الآن يمكنك استخدام sections-setup.html!")
