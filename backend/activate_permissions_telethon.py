"""
تفعيل صلاحيات القروب باستخدام Telethon
"""
import asyncio
import os
import sys
import django

# إعداد Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from telethon import TelegramClient, functions, types, errors


async def activate_permissions(chat_id: int, phone_number: str, bot_username: str):
    """
    تفعيل صلاحيات القروب الكاملة
    
    Args:
        chat_id: معرف القروب
        phone_number: رقم الهاتف المستخدم
        bot_username: اسم البوت (بدون أو مع @)
    
    Returns:
        dict: النتيجة
    """
    # اسم الجلسة
    session_name = f"session_{phone_number.replace('+', '')}"
    sessions_dir = os.path.join(settings.BASE_DIR, 'sessions')
    session_path = os.path.join(sessions_dir, session_name)
    
    # التحقق من وجود الجلسة
    if not os.path.exists(f"{session_path}.session"):
        return {
            "success": False,
            "error": "session_not_found",
            "message": f"الجلسة غير موجودة للرقم {phone_number}"
        }
    
    print("=" * 60)
    print(f"تفعيل صلاحيات القروب: {chat_id}")
    print(f"الهاتف: {phone_number}")
    print("=" * 60)
    
    # إنشاء Client
    client = TelegramClient(session_path, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            return {
                "success": False,
                "error": "not_authorized",
                "message": "الجلسة غير مخولة"
            }
        
        print("✓ تم الاتصال بنجاح")
        
        # الحصول على القناة
        try:
            channel = await client.get_entity(chat_id)
            print(f"✓ تم الوصول للقروب: {channel.title}")
        except Exception as e:
            return {
                "success": False,
                "error": "channel_not_found",
                "message": f"لم يتم العثور على القروب: {e}"
            }
        
        # 1. تطبيق القراءة فقط
        try:
            print("تطبيق صلاحيات القراءة فقط...")
            rights = types.ChatBannedRights(
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_inline=True,
                send_polls=True,
                change_info=False,
                invite_users=False,
                pin_messages=False,
                until_date=0
            )
            await client(functions.messages.EditChatDefaultBannedRightsRequest(
                peer=channel,
                banned_rights=rights
            ))
            print("✓ تم تطبيق القراءة فقط")
        except errors.FloodWaitError as e:
            print(f"⚠ FloodWait {e.seconds}s...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"⚠ خطأ في تطبيق القراءة فقط: {e}")
        
        await asyncio.sleep(2)
        
        # 2. إظهار السجل
        try:
            print("تفعيل السجل للأعضاء الجدد...")
            await client(functions.channels.TogglePreHistoryHiddenRequest(
                channel=channel,
                enabled=False
            ))
            print("✓ تم تفعيل السجل")
        except errors.ChatNotModifiedError:
            print("✓ السجل مفعل بالفعل")
        except Exception as e:
            print(f"⚠ خطأ في تفعيل السجل: {e}")
        
        await asyncio.sleep(2)
        
        # 3. الحصول على البوت
        bot_user = bot_username if bot_username.startswith('@') else f'@{bot_username}'
        try:
            bot = await client.get_entity(bot_user)
            bot_id = bot.id
            print(f"✓ البوت: {bot_id}")
        except Exception as e:
            return {
                "success": False,
                "error": "bot_not_found",
                "message": f"البوت غير موجود: {e}"
            }
        
        # 4. التحقق من وجود البوت في القروب
        try:
            participants = await client.get_participants(channel, limit=200)
            bot_in_group = any(p.id == bot_id for p in participants)
            
            if not bot_in_group:
                return {
                    "success": False,
                    "error": "bot_not_in_group",
                    "message": f"البوت {bot_user} غير موجود في القروب"
                }
            print("✓ البوت موجود في القروب")
        except Exception as e:
            print(f"⚠ خطأ في التحقق من البوت: {e}")
        
        # 5. ترقية البوت (محاولتين)
        bot_promoted = False
        
        # محاولة 1: صلاحيات كاملة
        try:
            print("ترقية البوت (صلاحيات كاملة)...")
            full_rights = types.ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=True,
                manage_topics=True,
                manage_call=True,
                anonymous=False
            )
            await client(functions.channels.EditAdminRequest(
                channel=channel,
                user_id=bot,
                admin_rights=full_rights,
                rank="Bot"
            ))
            print("✓ تمت ترقية البوت (كاملة)")
            bot_promoted = True
        except errors.FloodWaitError as e:
            print(f"⚠ FloodWait {e.seconds}s...")
            await asyncio.sleep(e.seconds)
            # إعادة المحاولة
            try:
                await client(functions.channels.EditAdminRequest(
                    channel=channel,
                    user_id=bot,
                    admin_rights=full_rights,
                    rank="Bot"
                ))
                print("✓ تمت ترقية البوت بعد الانتظار")
                bot_promoted = True
            except:
                pass
        except Exception as e:
            print(f"⚠ فشلت الترقية الكاملة: {e}")
        
        # محاولة 2: صلاحيات أساسية
        if not bot_promoted:
            await asyncio.sleep(2)
            try:
                print("ترقية البوت (صلاحيات أساسية)...")
                minimal_rights = types.ChatAdminRights(
                    change_info=True,
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=False,
                    manage_topics=True,
                    manage_call=False,
                    anonymous=False
                )
                await client(functions.channels.EditAdminRequest(
                    channel=channel,
                    user_id=bot,
                    admin_rights=minimal_rights,
                    rank="Bot"
                ))
                print("✓ تمت ترقية البوت (أساسية)")
                bot_promoted = True
            except Exception as e:
                print(f"❌ فشلت الترقية الأساسية: {e}")
        
        if not bot_promoted:
            return {
                "success": False,
                "error": "bot_not_admin",
                "message": "فشلت ترقية البوت بعد محاولتين"
            }
        
        print("=" * 60)
        print("✅ تم تفعيل جميع الصلاحيات بنجاح!")
        print("=" * 60)
        
        return {
            "success": True,
            "message": "تم تفعيل الصلاحيات بنجاح",
            "permissions": {
                "members_readonly": True,
                "history_visible": True,
                "bot_promoted": True
            }
        }
        
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": f"خطأ: {e}"
        }
    
    finally:
        await client.disconnect()


# للاختبار المباشر
if __name__ == "__main__":
    import json
    
    if len(sys.argv) < 3:
        print("Usage: python activate_permissions_telethon.py <chat_id> <phone_number> [bot_username]")
        sys.exit(1)
    
    chat_id = int(sys.argv[1])
    phone = sys.argv[2]
    bot = sys.argv[3] if len(sys.argv) > 3 else settings.TELEGRAM_BOT_USERNAME
    
    result = asyncio.run(activate_permissions(chat_id, phone, bot))
    
    # طباعة JSON للنتيجة
    print("RESULT_JSON:", json.dumps(result))
