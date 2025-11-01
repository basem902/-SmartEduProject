import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration, SchoolGrade

# احصل على اسم المدرسة الصحيح من المستخدم
print("\n🏫 تحديث اسم المدرسة للطلاب")
print("=" * 50)

# عرض الأسماء الحالية
grades = SchoolGrade.objects.all()
print(f"\n📚 الصفوف الموجودة ({grades.count()}):")
for grade in grades:
    print(f"  - {grade.display_name}")
    print(f"    المدرسة الحالية: {grade.school_name}")
    print(f"    عدد الطلاب: {grade.registered_students.count()}")

print("\n" + "=" * 50)
new_school_name = input("✏️  أدخل اسم المدرسة الصحيح (أو اضغط Enter للإلغاء): ").strip()

if new_school_name:
    # تحديث الصفوف
    updated_grades = grades.update(school_name=new_school_name)
    print(f"✅ تم تحديث {updated_grades} صف")
    
    # تحديث الطلاب
    students = StudentRegistration.objects.all()
    updated_students = students.update(school_name=new_school_name)
    print(f"✅ تم تحديث {updated_students} طالب")
    
    print(f"\n🎉 تم تغيير اسم المدرسة إلى: {new_school_name}")
else:
    print("❌ تم الإلغاء")
