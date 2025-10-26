#!/usr/bin/env python
"""
تصحيح chat_id للقروبات
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup

print("🔧 تصحيح chat_id...")

groups = TelegramGroup.objects.filter(chat_id__isnull=False)

for group in groups:
    old_chat_id = group.chat_id
    
    # تحويل إلى سالب إذا كان موجب
    if old_chat_id > 0:
        # Telegram Supergroup format: -100{chat_id}
        new_chat_id = -1000000000000 - old_chat_id
        
        group.chat_id = new_chat_id
        group.save()
        
        print(f"✅ {group.group_name}")
        print(f"   {old_chat_id} → {new_chat_id}")
    else:
        print(f"⏭️ {group.group_name} (already negative)")

print("\n✅ اكتمل!")
