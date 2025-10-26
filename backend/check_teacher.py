#!/usr/bin/env python
"""
فحص وجود Teacher في قاعدة البيانات
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import Teacher
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 50)
print("📊 إحصائيات المستخدمين والمعلمين")
print("=" * 50)

users = User.objects.all()
teachers = Teacher.objects.all()

print(f"\n👥 Users: {users.count()}")
for user in users[:10]:
    has_teacher = hasattr(user, 'teacher_profile')
    print(f"   - {user.email} (id={user.id}) {'✅ مربوط' if has_teacher else '❌ غير مربوط'}")

print(f"\n👨‍🏫 Teachers: {teachers.count()}")
for teacher in teachers[:10]:
    user_linked = "✅ مربوط" if teacher.user else "❌ غير مربوط"
    print(f"   - {teacher.email} (id={teacher.id}) {user_linked}")

print("\n" + "=" * 50)

# التحقق من التطابق
print("\n🔍 فحص التطابق:")
for user in users:
    teacher = Teacher.objects.filter(email=user.email).first()
    if teacher:
        if hasattr(user, 'teacher_profile'):
            print(f"✅ {user.email}: User و Teacher مربوطان")
        else:
            print(f"⚠️ {user.email}: Teacher موجود لكن غير مربوط بـ User")
            print(f"   → Teacher ID: {teacher.id}, User ID: {user.id}")
            print(f"   → حل: ربطهما معاً")
    else:
        print(f"❌ {user.email}: User موجود لكن لا يوجد Teacher")
        print(f"   → حل: إنشاء Teacher record")

print("\n" + "=" * 50)
