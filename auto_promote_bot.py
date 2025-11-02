"""
ترقية البوت تلقائياً في جميع القروبات
"""
import os
import sys
import asyncio
from pyrogram import Client
from pyrogram.types import ChatPrivileges
from pyrogram.errors import UserNotParticipant, ChannelPrivate, ChatAdminRequired

# إعداد Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.conf import settings
from apps.sections.models import TelegramGroup

BOT_USERNAME = settings.TELEGRAM_BOT_USERNAME.replace('@', '')
API_ID = settings.TELEGRAM_API_ID
API_HASH = settings.TELEGRAM_API_HASH

async def promote_bot_in_group(client, chat_id, bot_id, group_name):
    """ترقية البوت في قروب واحد"""
    try:
        # التحقق من حالة البوت الحالية
        member = await client.get_chat_member(chat_id, bot_id)
        
        if member.status.name == "ADMINISTRATOR":
            print(f"   ✅ البوت مشرف بالفعل")
            return True
            
        elif member.status.name == "OWNER":
            print(f"   👑 البوت مالك القروب")
            return True
            
        elif member.status.name == "MEMBER":
            print(f"   ⚡ البوت عضو عادي → جاري الترقية...")
            
            # محاولة 1: صلاحيات كاملة
            try:
                await client.promote_chat_member(
                    chat_id,
                    bot_id,
                    privileges=ChatPrivileges(
                        can_manage_chat=True,
                        can_delete_messages=True,
                        can_manage_video_chats=True,
                        can_restrict_members=True,
                        can_promote_members=False,
                        can_change_info=True,
                        can_invite_users=True,
                        can_pin_messages=True,
                        can_post_messages=True,
                        can_manage_topics=True
                    )
                )
                print(f"   ✅ تمت الترقية بنجاح!")
                return True
                
            except Exception as e1:
                print(f"   ⚠️  المحاولة الأولى فشلت: {e1}")
                
                # محاولة 2: صلاحيات أقل
                try:
                    await asyncio.sleep(2)
                    await client.promote_chat_member(
                        chat_id,
                        bot_id,
                        privileges=ChatPrivileges(
                            can_delete_messages=True,
                            can_invite_users=True,
                            can_pin_messages=True,
                            can_change_info=True,
                            can_post_messages=True
                        )
                    )
                    print(f"   ✅ تمت الترقية بصلاحيات محدودة")
                    return True
                    
                except Exception as e2:
                    print(f"   ❌ فشلت الترقية: {e2}")
                    return False
        else:
            print(f"   ❓ حالة غير معروفة: {member.status.name}")
            return False
            
    except UserNotParticipant:
        print(f"   ❌ البوت ليس في القروب - يجب إضافته أولاً")
        return False
        
    except ChatAdminRequired:
        print(f"   ❌ أنت لست مشرف في هذا القروب")
        return False
        
    except ChannelPrivate:
        print(f"   ⚠️  لا يمكن الوصول للقروب")
        return False
        
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False

async def auto_promote_all():
    """ترقية البوت في جميع القروبات"""
    
    # البحث عن session المحفوظ في مجلد backend/sessions
    backend_dir = os.path.join(BASE_DIR, 'backend')
    session_dir = os.path.join(backend_dir, 'sessions')
    
    # البحث عن أي session متاح
    session_file = None
    if os.path.exists(session_dir):
        for filename in os.listdir(session_dir):
            if filename.endswith('.session') and 'session_' in filename:
                session_file = os.path.join(session_dir, filename.replace('.session', ''))
                print(f"✅ وجدت session: {filename}")
                break
    
    if not session_file or not os.path.exists(session_file + '.session'):
        print("\n❌ لا توجد session محفوظة!")
        print("\n💡 الحل:")
        print("   1. اذهب إلى sections-setup.html")
        print("   2. اضغط 'إنشاء قروبات جديدة'")
        print("   3. سجّل الدخول بحسابك")
        print("   4. بعد ذلك شغّل هذا السكريبت مرة أخرى\n")
        return
    
    print("\n" + "=" * 80)
    print("🤖 ترقية البوت التلقائية في جميع القروبات")
    print("=" * 80)
    
    client = Client(
        name=session_file,
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=None
    )
    
    async with client:
        # جلب معلومات البوت
        try:
            bot = await client.get_users(f"@{BOT_USERNAME}")
            print(f"\n🤖 البوت: @{BOT_USERNAME} (ID: {bot.id})\n")
        except Exception as e:
            print(f"\n❌ خطأ في الحصول على معلومات البوت: {e}\n")
            return
        
        # جلب جميع القروبات من Database
        groups = TelegramGroup.objects.filter(is_active=True)
        
        if not groups.exists():
            print("⚠️  لا توجد قروبات في Database\n")
            return
        
        print(f"📊 العدد الإجمالي: {groups.count()} قروب\n")
        print("=" * 80)
        
        success_count = 0
        failed_count = 0
        already_admin = 0
        
        for i, group in enumerate(groups, 1):
            print(f"\n[{i}/{groups.count()}] 📱 {group.group_name}")
            print(f"         Chat ID: {group.chat_id}")
            
            result = await promote_bot_in_group(client, group.chat_id, bot.id, group.group_name)
            
            if result:
                # تحديث Database
                member = await client.get_chat_member(group.chat_id, bot.id)
                if member.status.name in ["ADMINISTRATOR", "OWNER"]:
                    group.is_bot_added = True
                    group.status = 'active'
                    group.save()
                    
                    if member.status.name == "ADMINISTRATOR":
                        success_count += 1
                    else:
                        already_admin += 1
            else:
                failed_count += 1
            
            # تأخير بين القروبات لتجنب Flood
            if i < groups.count():
                await asyncio.sleep(3)
        
        # الملخص النهائي
        print("\n" + "=" * 80)
        print("📊 ملخص النتائج:")
        print("=" * 80)
        print(f"   ✅ تمت الترقية بنجاح: {success_count}")
        print(f"   👑 كان مشرف مسبقاً: {already_admin}")
        print(f"   ❌ فشلت الترقية: {failed_count}")
        print(f"   📊 الإجمالي: {groups.count()}")
        print("=" * 80 + "\n")
        
        if failed_count > 0:
            print("💡 للقروبات الفاشلة:")
            print("   • تأكد أنك مشرف في القروب")
            print("   • أضف البوت يدوياً إذا لم يكن موجوداً")
            print("   • رقّه يدوياً من إعدادات القروب\n")

if __name__ == '__main__':
    print("\n⚡ بدء الترقية التلقائية...\n")
    asyncio.run(auto_promote_all())
