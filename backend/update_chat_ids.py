#!/usr/bin/env python
"""
تحديث chat_id للقروبات الموجودة باستخدام Telethon
"""
import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup
from django.conf import settings
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest
import re

# الحصول على API credentials من settings
API_ID = getattr(settings, 'TELEGRAM_API_ID', None)
API_HASH = getattr(settings, 'TELEGRAM_API_HASH', None)

if not API_ID or not API_HASH:
    print("❌ TELEGRAM_API_ID و TELEGRAM_API_HASH غير موجودين في settings!")
    print("   → أضفهما في core/settings.py")
    exit(1)

async def get_chat_id_from_invite_link(client, invite_link):
    """
    الحصول على chat_id من رابط الدعوة
    """
    try:
        # استخراج hash من رابط الدعوة
        # https://t.me/+xxxxx → xxxxx
        match = re.search(r't\.me/\+(.+)', invite_link)
        if not match:
            print(f"   ❌ رابط غير صحيح: {invite_link}")
            return None
        
        invite_hash = match.group(1)
        
        print(f"   🔗 محاولة الانضمام باستخدام: {invite_hash[:20]}...")
        
        # الانضمام للقروب
        result = await client(ImportChatInviteRequest(invite_hash))
        
        # الحصول على chat_id
        chat = result.chats[0]
        chat_id = chat.id
        
        # تحويل إلى سالب (Telegram supergroups)
        if chat_id > 0:
            chat_id = -1000000000000 - chat_id
        
        print(f"   ✅ chat_id: {chat_id}")
        
        return chat_id
        
    except Exception as e:
        print(f"   ❌ خطأ: {str(e)}")
        return None

async def update_all_chat_ids(phone_number):
    """
    تحديث chat_id لجميع القروبات
    """
    print("=" * 60)
    print("📱 تحديث chat_id للقروبات")
    print("=" * 60)
    
    # إنشاء Telegram client
    client = TelegramClient('update_chat_ids_session', API_ID, API_HASH)
    
    await client.start(phone=phone_number)
    print(f"\n✅ تم تسجيل الدخول بنجاح!")
    
    # جلب القروبات بدون chat_id
    groups = TelegramGroup.objects.filter(chat_id__isnull=True)
    
    print(f"\n📊 عدد القروبات: {groups.count()}")
    
    updated_count = 0
    failed_count = 0
    
    for i, group in enumerate(groups, 1):
        print(f"\n[{i}/{groups.count()}] {group.group_name}")
        print(f"   Section: {group.section.section_name}")
        
        chat_id = await get_chat_id_from_invite_link(client, group.invite_link)
        
        if chat_id:
            # تحديث Database
            group.chat_id = chat_id
            group.is_bot_added = False  # سنضيف البوت لاحقاً
            group.status = 'created'
            group.save()
            
            print(f"   💾 تم الحفظ في Database")
            updated_count += 1
        else:
            failed_count += 1
        
        # انتظار 2 ثانية بين كل قروب
        await asyncio.sleep(2)
    
    await client.disconnect()
    
    print("\n" + "=" * 60)
    print("📈 النتائج:")
    print("=" * 60)
    print(f"✅ تم التحديث: {updated_count}")
    print(f"❌ فشل: {failed_count}")
    print(f"📊 المجموع: {groups.count()}")
    
    # التحقق النهائي
    remaining = TelegramGroup.objects.filter(chat_id__isnull=True).count()
    print(f"\n📊 القروبات المتبقية بدون chat_id: {remaining}")
    
    if remaining == 0:
        print("\n🎉 جميع القروبات الآن لديها chat_id!")
    
    print("\n" + "=" * 60)

def main():
    """
    النقطة الرئيسية للتشغيل
    """
    print("=" * 60)
    print("🚀 سكريبت تحديث chat_id")
    print("=" * 60)
    
    # طلب رقم الهاتف
    phone = input("\n📱 أدخل رقم هاتفك (مع +966): ")
    
    if not phone.startswith('+'):
        phone = '+' + phone
    
    print(f"\n✅ سيتم استخدام: {phone}")
    print("\n⚠️ تأكد من:")
    print("   1. أنك قد انضممت لهذه القروبات مسبقاً")
    print("   2. أو لديك الرابط صحيح")
    
    confirm = input("\nهل تريد المتابعة؟ (yes/no): ")
    
    if confirm.lower() in ['yes', 'y', 'نعم']:
        # تشغيل async function
        asyncio.run(update_all_chat_ids(phone))
    else:
        print("\n❌ تم الإلغاء")

if __name__ == '__main__':
    main()
