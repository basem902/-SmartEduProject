import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import Section

print("\n🔄 تحديث عدد الطلاب في جميع الشُعب...")
print("=" * 60)

sections = Section.objects.all()
updated = 0

for section in sections:
    real_count = section.registered_students.count()
    old_count = section.total_students
    
    if real_count != old_count:
        section.total_students = real_count
        section.save()
        updated += 1
        print(f"✅ {section.section_name}: {old_count} → {real_count}")
    else:
        print(f"✓  {section.section_name}: {real_count} (لا تغيير)")

print("\n" + "=" * 60)
print(f"✅ تم تحديث {updated} شعبة")
print(f"📊 إجمالي الطلاب: {sum(s.total_students for s in Section.objects.all())}")
