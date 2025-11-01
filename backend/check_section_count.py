import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import Section, StudentRegistration

print("\n📊 فحص عدد الطلاب في الشُعب:")
print("=" * 60)

sections = Section.objects.all()
for section in sections:
    real_count = section.registered_students.count()
    stored_count = section.total_students
    
    print(f"\n📖 الشعبة: {section.section_name}")
    print(f"   الصف: {section.grade.display_name}")
    print(f"   ✅ العدد الحقيقي في Database: {real_count}")
    print(f"   {'❌' if stored_count != real_count else '✅'} total_students: {stored_count}")
    
    if stored_count != real_count:
        print(f"   ⚠️  مطلوب تحديث!")

print("\n" + "=" * 60)
print(f"\n📈 إجمالي الطلاب المسجلين: {StudentRegistration.objects.count()}")
