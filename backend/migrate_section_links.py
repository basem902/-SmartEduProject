#!/usr/bin/env python
"""
نقل بيانات القروبات من SectionLink إلى TelegramGroup
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import SectionLink, TelegramGroup
from django.utils import timezone

print("=" * 60)
print("🔄 نقل بيانات القروبات من SectionLink إلى TelegramGroup")
print("=" * 60)

# جلب جميع SectionLinks التي تحتوي على telegram_link
section_links = SectionLink.objects.filter(
    platform='telegram',
    telegram_link__isnull=False
).exclude(telegram_link='')

print(f"\n📊 عدد SectionLinks المراد نقلها: {section_links.count()}")

created_count = 0
updated_count = 0
skipped_count = 0
errors = []

for link in section_links:
    try:
        section = link.section
        
        # التحقق من عدم وجود TelegramGroup
        telegram_group, created = TelegramGroup.objects.get_or_create(
            section=section,
            defaults={
                'group_name': f"{section.grade.display_name} - {section.section_name}",
                'invite_link': link.telegram_link,
                'created_by_phone': section.grade.teacher.phone or 'unknown',
                'status': 'active',
                'is_bot_added': False,
                'creation_metadata': {
                    'migrated_from': 'SectionLink',
                    'original_link_id': link.id,
                    'migrated_at': timezone.now().isoformat()
                }
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ تم إنشاء: {section.section_name} (Grade: {section.grade.id})")
            print(f"   Link: {telegram_group.invite_link[:50]}...")
        else:
            # تحديث السجل الموجود
            telegram_group.invite_link = link.telegram_link
            telegram_group.group_name = f"{section.grade.display_name} - {section.section_name}"
            telegram_group.status = 'active'
            telegram_group.save()
            updated_count += 1
            print(f"🔄 تم التحديث: {section.section_name} (Grade: {section.grade.id})")
            
    except Exception as e:
        skipped_count += 1
        error_msg = f"❌ خطأ في {link.section.section_name}: {str(e)}"
        errors.append(error_msg)
        print(error_msg)

print("\n" + "=" * 60)
print("📈 النتائج النهائية:")
print("=" * 60)
print(f"✅ تم الإنشاء: {created_count}")
print(f"🔄 تم التحديث: {updated_count}")
print(f"❌ تم التخطي: {skipped_count}")
print(f"📊 المجموع: {section_links.count()}")

if errors:
    print("\n⚠️ الأخطاء:")
    for error in errors:
        print(f"   {error}")

print("\n" + "=" * 60)
print("🎉 اكتمل النقل!")
print("=" * 60)

# التحقق النهائي
telegram_groups = TelegramGroup.objects.all()
print(f"\n📱 عدد TelegramGroups الآن: {telegram_groups.count()}")

# عرض نموذج
print("\n📋 نموذج من البيانات المنقولة:")
for tg in telegram_groups[:3]:
    print(f"   - {tg.group_name}")
    print(f"     Section: {tg.section.section_name}")
    print(f"     Link: {tg.invite_link[:50]}...")
    print(f"     Status: {tg.status}")
    print()
