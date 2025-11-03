import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration

students = StudentRegistration.objects.all()

print(f"\n📊 عدد الطلاب في Database: {students.count()}\n")

if students.exists():
    for s in students:
        print(f"ID: {s.id}")
        print(f"الاسم: {s.full_name}")
        print(f"الشعبة: {s.section.section_name}")
        print(f"انضم للتليجرام: {s.joined_telegram}")
        print(f"Username: {s.telegram_username or 'غير متوفر'}")
        print(f"User ID: {s.telegram_user_id or 'غير متوفر'}")
        print("-" * 60)
else:
    print("⚠️  لا يوجد طلاب في Database")
    print("\nالحل:")
    print("1. أضف طلاب من: http://localhost:5500/pages/add-students.html")
    print("2. أو ارفع Excel من نفس الصفحة")
