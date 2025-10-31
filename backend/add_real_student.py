"""
➕ إضافة طالب حقيقي للاختبار
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration, Section, TelegramGroup
from apps.accounts.models import Teacher

print("=" * 60)
print("➕ إضافة طالب حقيقي")
print("=" * 60)
print()

# المعلومات المطلوبة
print("📋 أدخل معلومات الطالب:")
print()

student_name = input("الاسم الكامل (رباعي): ")
telegram_username = input("Telegram Username (بدون @): ")
telegram_id = input("Telegram User ID (اختياري، اضغط Enter للتخطي): ")

# اختيار الشعبة
print()
print("📖 الشُعب المتاحة:")
sections = Section.objects.all()
for i, section in enumerate(sections, 1):
    print(f"   {i}. {section.grade.display_name} - {section.section_name}")

section_choice = int(input("\nاختر رقم الشعبة: ")) - 1
selected_section = sections[section_choice]

print()
print(f"✅ الشعبة المختارة: {selected_section}")

# القروب
telegram_group = selected_section.telegram_group
if telegram_group:
    print(f"📱 القروب: {telegram_group.group_name}")
    print(f"   Chat ID: {telegram_group.chat_id}")
    
    # تحديث Chat ID إذا لزم الأمر
    update_chat_id = input("\nهل تريد تحديث Chat ID؟ (y/n): ")
    if update_chat_id.lower() == 'y':
        new_chat_id = input("أدخل Chat ID الجديد: ")
        telegram_group.chat_id = int(new_chat_id)
        telegram_group.save()
        print(f"✅ تم تحديث Chat ID إلى: {new_chat_id}")
else:
    print("⚠️ لا يوجد قروب مرتبط بهذه الشعبة")
    create_group = input("هل تريد إنشاء قروب؟ (y/n): ")
    if create_group.lower() == 'y':
        group_name = input("اسم القروب: ")
        chat_id = input("Chat ID: ")
        invite_link = input("رابط الدعوة: ")
        
        telegram_group = TelegramGroup.objects.create(
            section=selected_section,
            group_name=group_name,
            chat_id=int(chat_id),
            invite_link=invite_link,
            created_by_phone='0500000001',
            status='created'
        )
        print(f"✅ تم إنشاء القروب: {group_name}")

# إنشاء الطالب
print()
print("💾 إنشاء الطالب...")

import re
def normalize_arabic_name(name):
    name = ' '.join(name.split())
    name = re.sub('[إأآا]', 'ا', name)
    name = re.sub('ى', 'ي', name)
    name = re.sub('ة', 'ه', name)
    return name.strip().lower()

teacher = Teacher.objects.first()

student = StudentRegistration.objects.create(
    teacher=teacher,
    grade=selected_section.grade,
    section=selected_section,
    full_name=student_name,
    normalized_name=normalize_arabic_name(student_name),
    telegram_username=telegram_username,
    telegram_user_id=int(telegram_id) if telegram_id else None,
    telegram_group=telegram_group,
    school_name=selected_section.grade.school_name,
    joined_telegram=bool(telegram_id),
)

print()
print("=" * 60)
print("✅ تم إضافة الطالب بنجاح!")
print("=" * 60)
print()
print("📊 معلومات الطالب:")
print(f"   الاسم: {student.full_name}")
print(f"   الاسم المُطبّع: {student.normalized_name}")
print(f"   الشعبة: {student.section.section_name}")
print(f"   الصف: {student.grade.display_name}")
print(f"   Telegram: @{student.telegram_username}")
if student.telegram_user_id:
    print(f"   User ID: {student.telegram_user_id}")
print(f"   القروب: {telegram_group.group_name if telegram_group else 'لا يوجد'}")
print()

print("🧪 الآن يمكنك اختبار:")
print("   1. صفحة التحقق:")
print(f"      http://localhost:5500/student-verify-demo.html")
print(f"      الاسم: {student.full_name}")
print()
print("   2. صفحة الإنتاج:")
print("      https://smartedu-basem.netlify.app/pages/submit-project.html")
print()
