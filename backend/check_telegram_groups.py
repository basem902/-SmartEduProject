#!/usr/bin/env python
"""
فحص جدول telegram_groups
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup, Section, SectionLink, SchoolGrade
from apps.accounts.models import Teacher

print("=" * 60)
print("📊 فحص جدول telegram_groups")
print("=" * 60)

# 1. عدد السجلات
telegram_groups = TelegramGroup.objects.all()
sections = Section.objects.all()
section_links = SectionLink.objects.all()
grades = SchoolGrade.objects.all()

print(f"\n📈 الإحصائيات:")
print(f"   - Grades: {grades.count()}")
print(f"   - Sections: {sections.count()}")
print(f"   - TelegramGroups: {telegram_groups.count()} ⚠️")
print(f"   - SectionLinks: {section_links.count()}")

# 2. عرض الـ Grades
print(f"\n🎓 الصفوف الدراسية:")
for grade in grades:
    sections_count = grade.sections.count()
    print(f"   - {grade} (id={grade.id})")
    print(f"     → Sections: {sections_count}")
    
    for section in grade.sections.all():
        # البحث عن TelegramGroup
        tg = TelegramGroup.objects.filter(section=section).first()
        sl = SectionLink.objects.filter(section=section, platform='telegram').first()
        
        print(f"       • {section.section_name} (id={section.id}):")
        print(f"         - TelegramGroup: {'✅ موجود' if tg else '❌ مفقود'}")
        if tg:
            print(f"           chat_id: {tg.chat_id}")
            print(f"           invite_link: {tg.invite_link}")
        
        print(f"         - SectionLink: {'✅ موجود' if sl else '❌ مفقود'}")
        if sl:
            print(f"           telegram_link: {sl.telegram_link}")

# 3. عرض TelegramGroups إن وُجدت
if telegram_groups.count() > 0:
    print(f"\n📱 TelegramGroups الموجودة:")
    for tg in telegram_groups:
        print(f"   - {tg.group_name} (Section: {tg.section})")
        print(f"     chat_id: {tg.chat_id}")
        print(f"     invite_link: {tg.invite_link}")
        print(f"     status: {tg.status}")
        print(f"     created: {tg.created_at}")
else:
    print(f"\n⚠️ لا توجد سجلات في TelegramGroups!")
    print(f"\n🔍 السبب المحتمل:")
    print(f"   1. لم يتم إنشاء القروبات بعد")
    print(f"   2. تم الحفظ في SectionLink بدلاً من TelegramGroup")
    print(f"   3. حدث خطأ أثناء الإنشاء")

# 4. فحص SectionLinks
if section_links.count() > 0:
    print(f"\n🔗 SectionLinks الموجودة:")
    for sl in section_links:
        print(f"   - {sl.section} ({sl.platform})")
        print(f"     telegram_link: {sl.telegram_link}")

print("\n" + "=" * 60)
