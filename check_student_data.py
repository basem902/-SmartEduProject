import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration, SchoolGrade

# فحص الطالب الأخير
student = StudentRegistration.objects.last()

if student:
    print("\n📊 بيانات الطالب:")
    print(f"  الاسم: {student.full_name}")
    print(f"  الاسم المطبع: {student.normalized_name}")
    print(f"  الجوال: {student.phone_number}")
    print(f"  المعلم: {student.teacher}")
    print(f"  الصف: {student.grade}")
    print(f"  الشعبة: {student.section}")
    print(f"  المدرسة: {student.school_name}")
    print(f"\n🔍 فحص الصف:")
    print(f"  Grade ID: {student.grade.id}")
    print(f"  Grade school_name: {student.grade.school_name}")
    print(f"  Grade teacher: {student.grade.teacher}")
    print(f"  Grade display_name: {student.grade.display_name}")
else:
    print("❌ لا يوجد طلاب في Database")
