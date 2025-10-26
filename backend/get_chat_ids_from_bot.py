#!/usr/bin/env python
"""
الحصول على chat_id من Telegram Bot للقروبات الموجودة
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup

print("=" * 60)
print("📱 تحديث chat_id للقروبات الموجودة")
print("=" * 60)

groups_without_chat_id = TelegramGroup.objects.filter(chat_id__isnull=True)

print(f"\n📊 القروبات بدون chat_id: {groups_without_chat_id.count()}")

if groups_without_chat_id.count() == 0:
    print("\n✅ جميع القروبات لديها chat_id!")
else:
    print("\n📋 القروبات التي تحتاج chat_id:")
    for group in groups_without_chat_id:
        print(f"\n   📌 {group.group_name}")
        print(f"      - ID: {group.id}")
        print(f"      - Section: {group.section.section_name}")
        print(f"      - Invite Link: {group.invite_link[:50]}...")
        print(f"      - Status: {group.status}")

print("\n" + "=" * 60)
print("💡 كيفية الحصول على chat_id:")
print("=" * 60)

print("""
🤖 **الطريقة الأولى: استخدام البوت (الأسهل)**

1. افتح Telegram
2. ابحث عن: @SmartEduProjectBot
3. اضغط Start
4. أرسل الأمر: /get_chat_id
5. افتح كل قروب واحد تلو الآخر
6. البوت سيرسل لك chat_id لكل قروب

📱 **الطريقة الثانية: من Bot API**

1. أضف البوت كـ Admin في جميع القروبات
2. استخدم getUpdates API:
   https://api.telegram.org/bot<TOKEN>/getUpdates
3. ابحث عن chat.id في الـ JSON

🔧 **الطريقة الثالثة: إعادة الإنشاء التلقائي**

1. احذف القروبات الحالية من Database
2. استخدم زر "📱 تيليجرام" في sections-manage.html
3. سيتم إنشاء قروبات جديدة مع chat_id تلقائياً

⚡ **الطريقة الرابعة: Script تلقائي (مُوصى)**

سأنشئ سكريبت يحصل على chat_id تلقائياً من Bot API
""")

print("\n" + "=" * 60)
print("❓ ماذا تريد أن تفعل؟")
print("=" * 60)
print("1. إنشاء سكريبت تلقائي للحصول على chat_id")
print("2. إعادة إنشاء القروبات تلقائياً (يحذف الحالية)")
print("3. حفظ chat_id يدوياً لكل قروب")
print("\n💡 أنصحك بالخيار 2 (إعادة الإنشاء التلقائي)")
