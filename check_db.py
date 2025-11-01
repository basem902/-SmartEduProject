"""Quick check for students in database"""
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration

students = StudentRegistration.objects.all()
print(f"\n📊 الطلاب في Database: {students.count()}")

for i, s in enumerate(students, 1):
    print(f"{i}. {s.full_name} ({s.section.section_name if s.section else '؟'})")

if students.count() == 0:
    print("\n❌ لا يوجد طلاب!")
    print("💡 اضغط 'حفظ الكل' في صفحة إضافة الطلاب\n")
