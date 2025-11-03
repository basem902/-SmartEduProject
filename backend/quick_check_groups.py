import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup, Section

sections = Section.objects.all()
groups = TelegramGroup.objects.all()

print(f'\n📊 الشُعب الموجودة: {sections.count()}')
print(f'📱 القروبات الموجودة: {groups.count()}\n')

for section in sections:
    try:
        group = section.telegram_group
        print(f'✅ {section.grade.display_name} - {section.section_name} → {group.group_name}')
    except:
        print(f'❌ {section.grade.display_name} - {section.section_name} → لا يوجد قروب')

print()
