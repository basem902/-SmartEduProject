import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration

students = StudentRegistration.objects.filter(full_name__contains='ريماس')

if not students.exists():
    print("❌ لا يوجد طالب باسم ريماس")
else:
    for s in students:
        print(f"\n📋 الطالب: {s.full_name}")
        print(f"   الصف: {s.grade.display_name}")
        print(f"   الشعبة: {s.section.section_name} (ID: {s.section.id})")
        
        try:
            group = s.section.telegram_group
            print(f"   ✅ القروب: {group.group_name}")
            print(f"   📱 رابط القروب: {group.invite_link}")
            print(f"   💬 Chat ID: {group.chat_id}")
        except Exception as e:
            print(f"   ❌ القروب: غير موجود")
            print(f"   الخطأ: {str(e)}")
