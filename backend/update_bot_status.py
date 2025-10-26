#!/usr/bin/env python
"""
تحديث حالة البوت لجميع القروبات
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup

print("🔄 تحديث حالة البوت...")

groups = TelegramGroup.objects.all()

for group in groups:
    group.is_bot_added = True
    group.is_bot_admin = True  # افترض أنك أضفته كـ Admin
    group.status = 'bot_added'
    group.save()
    print(f"✅ {group.group_name}")

print(f"\n✅ تم تحديث {groups.count()} قروبات")
print("🎉 الآن يمكنك إرسال الإشعارات!")
