"""
Script مستقل لإنشاء قروبات تيليجرام
يعمل خارج Django تماماً
"""
import os
import sys
import django
import asyncio
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# إعداد Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from pyrogram import Client, errors
from pyrogram.types import ChatPrivileges
from pyrogram import raw
import requests


def normalize_chat_id(chat_id):
    """
    تحويل chat_id إلى التنسيق الصحيح
    Supergroups يجب أن تبدأ بـ -100
    """
    if not chat_id:
        return None
    
    # تحويل إلى int
    chat_id = int(chat_id)
    
    # إذا كان موجب، حوله إلى سالب بالتنسيق الصحيح
    if chat_id > 0:
        # Supergroup IDs in Telegram start with -100
        return -(1000000000000 + chat_id)
    
    # إذا كان سالب بالفعل
    if str(chat_id).startswith('-100'):
        # بالفعل بالتنسيق الصحيح
        return chat_id
    
    # إذا كان سالب لكن بتنسيق خاطئ (مثل -103...)
    # نحوله للإيجابي ثم نطبق التنسيق الصحيح
    abs_id = abs(chat_id)
    return -(1000000000000 + abs_id)


def send_bot_message(bot_token, chat_id, text, parse_mode='Markdown'):
    """إرسال رسالة من البوت باستخدام Bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    response = requests.post(url, data=data)
    return response.json()


def pin_bot_message(bot_token, chat_id, message_id):
    """تثبيت رسالة باستخدام Bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/pinChatMessage"
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'disable_notification': False
    }
    response = requests.post(url, data=data)
    return response.json()


def promote_bot_admin(bot_token, chat_id, user_id):
    """ترقية البوت إلى مدير باستخدام Bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/promoteChatMember"
    data = {
        'chat_id': chat_id,
        'user_id': user_id,
        'can_manage_chat': True,
        'can_delete_messages': True,
        'can_manage_video_chats': True,
        'can_restrict_members': True,
        'can_promote_members': False,
        'can_change_info': True,
        'can_invite_users': True,
        'can_pin_messages': True,
        'can_post_messages': True
    }
    response = requests.post(url, data=data)
    return response.json()


async def promote_bot_with_retry(client, chat_id, bot_user_id, bot_token=None, max_retries=2):
    """
    ترقية البوت مع retry logic (محاولتين)
    مستوحى من منطق Telethon script
    
    المحاولة 1: صلاحيات كاملة
    المحاولة 2: صلاحيات أساسية
    المحاولة 3: Bot API (إذا توفر token)
    """
    from pyrogram import errors
    
    # المحاولة 1: صلاحيات كاملة
    print(f"   [PROMOTE] Attempting full privileges...")
    try:
        await client.promote_chat_member(
            chat_id,
            bot_user_id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=True,  # محاولة إعطاء هذه الصلاحية
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_post_messages=True,
                can_edit_messages=False,
                can_manage_topics=True
            )
        )
        print(f"   [OK] Bot promoted with FULL privileges")
        return True
    except errors.FloodWait as e:
        print(f"   [WAIT] FloodWait {e.value}s, waiting...")
        await asyncio.sleep(e.value)
        # إعادة المحاولة بعد الانتظار
        try:
            await client.promote_chat_member(chat_id, bot_user_id, privileges=ChatPrivileges(can_delete_messages=True))
            print(f"   [OK] Bot promoted after FloodWait")
            return True
        except Exception:
            pass
    except Exception as e:
        print(f"   [WARN] Full promotion failed: {e}")
    
    # المحاولة 2: صلاحيات أساسية (مخففة)
    print(f"   [PROMOTE] Attempting minimal privileges...")
    await asyncio.sleep(2)
    try:
        await client.promote_chat_member(
            chat_id,
            bot_user_id,
            privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=True,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_post_messages=True
            )
        )
        print(f"   [OK] Bot promoted with MINIMAL privileges")
        return True
    except Exception as e:
        print(f"   [WARN] Minimal promotion also failed: {e}")
    
    # المحاولة 3: Bot API (إذا توفر)
    if bot_token:
        print(f"   [PROMOTE] Attempting via Bot API...")
        await asyncio.sleep(2)
        try:
            result = promote_bot_admin(bot_token, chat_id, bot_user_id)
            if result.get('ok'):
                print(f"   [OK] Bot promoted via Bot API")
                return True
            else:
                print(f"   [WARN] Bot API failed: {result.get('description')}")
        except Exception as e:
            print(f"   [WARN] Bot API exception: {e}")
    
    print(f"   [FAIL] All promotion attempts failed")
    return False


async def create_groups(api_id, api_hash, phone_number, grade_name, subject_name, sections, school_name=None, teacher_name=None, bot_username=None, bot_token=None):
    """إنشاء القروبات"""
    
    # استخدام الـ session المحفوظ من telegram_session_manager
    from apps.sections.telegram_session_manager import session_manager
    
    # التحقق من وجود session
    if not session_manager.is_session_exists(phone_number):
        raise Exception(f"لا يوجد session محفوظ للرقم {phone_number}. يجب ربط الحساب أولاً!")
    
    # الحصول على session string المُشفر
    session_string = session_manager.get_session_string(phone_number)
    if not session_string:
        raise Exception(f"فشل تحميل session للرقم {phone_number}")
    
    print(f"[OK] Loaded session for {phone_number}")
    
    # إنشاء Client باستخدام session_string
    client = Client(
        name="telegram_groups_client",
        api_id=api_id,
        api_hash=api_hash,
        session_string=session_string,
        in_memory=True  # استخدام in-memory لتجنب database lock
    )
    
    results = []
    
    try:
        # الاتصال بدون طلب كود (نستخدم session موجود)
        await client.connect()
        print(f"[OK] Connected to Telegram using saved session")
        
        # الحصول على قائمة القروبات الموجودة لتجنب التكرار
        existing_groups = {}
        print(f"[INFO] Checking existing groups...")
        async for dialog in client.get_dialogs():
            if dialog.chat.type in ["group", "supergroup"]:
                existing_groups[dialog.chat.title] = dialog.chat.id
        print(f"[INFO] Found {len(existing_groups)} existing groups")
        
        for i, section in enumerate(sections):
            group_name = f"{grade_name} {section} - {subject_name}"
            
            description = f"قروب {subject_name}\n"
            description += f"الصف: {grade_name} - الشعبة {section}\n"
            if school_name:
                description += f"المدرسة: {school_name}\n"
            description += "\nمرحباً بكم في قروب الدراسة!"
            
            print(f"\n[{i+1}/{len(sections)}] Processing group: {group_name}")
            
            # التحقق من وجود القروب
            if group_name in existing_groups:
                raw_chat_id = existing_groups[group_name]
                chat_id = normalize_chat_id(raw_chat_id)
                print(f"   [SKIP] Group already exists (ID: {raw_chat_id} → {chat_id})")
                
                try:
                    # تطبيق صلاحيات Read-Only على القروب الموجود
                    print(f"   [PERMISSIONS] Applying read-only mode to existing group...")
                    await asyncio.sleep(3)  # انتظار قبل تطبيق الصلاحيات
                    from pyrogram.types import ChatPermissions
                    try:
                        await client.set_chat_permissions(
                            chat_id,
                            ChatPermissions(
                                can_send_messages=False,
                                can_send_media_messages=False,
                                can_send_polls=False,
                                can_send_other_messages=False,
                                can_add_web_page_previews=False,
                                can_change_info=False,
                                can_invite_users=False,
                                can_pin_messages=False
                            )
                        )
                        print(f"   [OK] Read-only mode applied to existing group")
                        await asyncio.sleep(2)  # انتظار بعد تطبيق الصلاحيات
                    except Exception as e:
                        print(f"   [WARN] Could not set permissions on existing group: {e}")
                    
                    # الحصول على رابط القروب الموجود
                    invite_link = await client.export_chat_invite_link(chat_id)
                    
                    results.append({
                        'success': True,
                        'section_name': section,
                        'group_name': group_name,
                        'chat_id': chat_id,
                        'invite_link': invite_link,
                        'already_exists': True,
                        'read_only': True
                    })
                    print(f"   [OK] Using existing group: {invite_link}")
                except Exception as e:
                    print(f"   [ERROR] Failed to get link: {e}")
                    results.append({
                        'success': False,
                        'section_name': section,
                        'group_name': group_name,
                        'error': f'Failed to access existing group: {str(e)}'
                    })
                continue
            
            try:
                # إنشاء القروب مع معالجة FloodWait
                print(f"   [CREATE] Creating new group...")
                try:
                    chat = await client.create_group(
                        title=group_name,
                        users=[]
                    )
                    print(f"   [OK] Group created (ID: {chat.id})")
                except errors.FloodWait as e:
                    print(f"   [WAIT] FloodWait {e.value}s before creating group, waiting...")
                    await asyncio.sleep(e.value)
                    # إعادة المحاولة
                    chat = await client.create_group(
                        title=group_name,
                        users=[]
                    )
                    print(f"   [OK] Group created after FloodWait (ID: {chat.id})")
                
                # الخطوة المهمة: إرسال رسالة التعليمات في Group العادي (قبل التحويل)
                # هذا يضمن أن السجل يبقى مرئياً للأعضاء الجدد!
                await asyncio.sleep(2)
                print(f"   [INSTRUCTIONS] Sending welcome message in basic group...")
                instructions_message = f"""
╔══════════════════════╗
║  🎓 مرحباً بكم! 🎓  ║
╚══════════════════════╝

📚 **المادة:** {subject_name}
🏫 **الصف:** {grade_name} - الشعبة {section}
👨‍🏫 **المعلم:** {teacher_name or '[سيتم التحديث]'}

─────────────────────

💎 **منصتك الشاملة للتميز الأكاديمي**

🎯 **المشاريع:**
   📢 إعلانات فورية
   📝 تعليمات واضحة
   🔗 روابط التسليم

📈 **التتبع الذكي:**
   ✅ إحصائيات دقيقة
   📊 متابعة الإنجاز
   🏆 نتائج وتقييمات

📚 **المحتوى التعليمي:**
   🎥 فيديوهات شرح
   📄 ملفات PDF
   🔗 مراجع ومصادر
   💡 نماذج وأمثلة

⏰ **التنبيهات الذكية:**
   🔔 تذكير بالمواعيد
   ⚡ إشعارات فورية
   ⏳ تحذير قبل الانتهاء

─────────────────────

⚠️ **إرشادات القروب:**
✓ القروب للقراءة فقط (Read-Only)
✓ فعّل الإشعارات للبقاء على اطلاع
✓ للاستفسارات: تواصل مع المعلم

─────────────────────

🌟 معاً نحو التميز والنجاح! 🌟

─────────────────────
🤖 Powered by SmartEdu
"""
                
                welcome_msg = None
                try:
                    # إرسال الرسالة في Group العادي (السجل مرئي افتراضياً)
                    welcome_msg = await client.send_message(chat.id, instructions_message)
                    print(f"   [OK] Welcome message sent in basic group")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"   [ERROR] Could not send welcome message: {e}")
                
                # الآن تحويل القروب إلى Supergroup (السجل يبقى مرئياً!)
                print(f"   [CONVERT] Converting to supergroup...")
                await asyncio.sleep(5)  # زيادة من 2 إلى 5 ثوان لتجنب Flood
                
                # إضافة وصف (هذا يحول القروب إلى supergroup تلقائياً)
                await client.set_chat_description(chat.id, description)
                await asyncio.sleep(3)  # انتظار بعد إضافة الوصف
                
                # الانتظار لتطبيق التحويل على خوادم تيليجرام
                await asyncio.sleep(3)
                
                # الحصول على معلومات القروب المحدثة
                from pyrogram.types import ChatPermissions
                chat = await client.get_chat(chat.id)
                print(f"   [OK] Converted to supergroup (ID: {chat.id})")
                
                # جعل المحادثات مرئية للأعضاء الجدد باستخدام Pyrogram raw API
                print(f"   [HISTORY] Making chat history visible to new members...")
                try:
                    # استخدام Pyrogram raw API لتفعيل الرؤية
                    await client.invoke(
                        raw.functions.channels.TogglePreHistoryHidden(
                            channel=await client.resolve_peer(chat.id),
                            enabled=False  # False = السجل مرئي للجميع
                        )
                    )
                    print(f"   [OK] Chat history is now VISIBLE to all new members!")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"   [ERROR] Could not toggle history visibility: {e}")
                    print(f"   [INFO] This might be a Telegram API issue, continuing anyway...")
                
                # تثبيت الرسالة (إذا تم إرسالها)
                if welcome_msg:
                    try:
                        await asyncio.sleep(2)
                        await client.pin_chat_message(chat.id, welcome_msg.id, disable_notification=False)
                        print(f"   [OK] Welcome message pinned successfully")
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"   [WARN] Could not pin message: {e}")
                
                # الآن تطبيق صلاحيات Read-Only (بعد إرسال وتثبيت التعليمات)
                print(f"   [PERMISSIONS] Setting read-only mode...")
                await asyncio.sleep(3)
                try:
                    await client.set_chat_permissions(
                        chat.id,
                        ChatPermissions(
                            can_send_messages=False,
                            can_send_media_messages=False,
                            can_send_polls=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False,
                            can_change_info=False,
                            can_invite_users=False,
                            can_pin_messages=False
                        )
                    )
                    print(f"   [OK] Read-only mode enabled (only admins can send)")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"   [WARN] Could not set permissions: {e}")
                
                # الحصول على رابط
                invite_link = await client.export_chat_invite_link(chat.id)
                
                # تحويل chat_id إلى التنسيق الصحيح (-100...)
                normalized_chat_id = normalize_chat_id(chat.id)
                print(f"   [INFO] Chat ID normalized: {chat.id} → {normalized_chat_id}")
                
                results.append({
                    'success': True,
                    'section_name': section,
                    'group_name': group_name,
                    'chat_id': normalized_chat_id,
                    'invite_link': invite_link,
                    'already_exists': False,
                    'read_only': True
                })
                
                print(f"   [OK] Created: {invite_link}")
                
                # إضافة البوت إذا كان موجود
                if bot_username:
                    try:
                        print(f"   [BOT] Adding bot @{bot_username}...")
                        await asyncio.sleep(3)  # انتظار قبل إضافة البوت
                        
                        # إضافة البوت للقروب
                        await client.add_chat_members(
                            chat_id=chat.id,
                            user_ids=[f"@{bot_username}"]
                        )
                        print(f"   [OK] Bot added")
                        
                        # انتظار لضمان التحديث على خوادم تيليجرام
                        await asyncio.sleep(5)  # زيادة الانتظار من 3 إلى 5 ثوان
                        
                        # الحصول على معلومات البوت
                        bot_user = await client.get_users(f"@{bot_username}")
                        
                        # ترقية البوت مع retry logic (محاولتين)
                        bot_promoted = await promote_bot_with_retry(client, chat.id, bot_user.id, bot_token)
                        
                        if bot_promoted:
                            print(f"   [INFO] Bot is now admin and can manage the group")
                        else:
                            print(f"   [WARN] Bot promotion failed after retries")
                        
                    except Exception as e:
                        print(f"   [WARN] Could not add/promote bot: {e}")
                
                # تأخير بين القروبات لتجنب Flood Control
                if i < len(sections) - 1:
                    print(f"   [WAIT] Waiting 30 seconds before next group...")
                    await asyncio.sleep(30)  # زيادة إلى 30 ثانية لتجنب FLOOD_WAIT
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'section_name': section,
                    'group_name': group_name,
                    'error': str(e)
                })
                print(f"   [FAIL] Error: {e}")
        
    finally:
        # استخدام disconnect بدلاً من stop (لأننا استخدمنا connect)
        try:
            await client.disconnect()
            print(f"[OK] Disconnected from Telegram")
        except Exception as e:
            print(f"[WARNING] Disconnect error: {e}")
    
    return results


if __name__ == '__main__':
    # قراءة البيانات من arguments
    if len(sys.argv) < 5:
        print("Usage: python create_groups_standalone.py <grade_name> <subject_name> <sections> <phone_number> [teacher_name]")
        print("مثال: python create_groups_standalone.py \"الصف الثالث متوسط\" \"المهارات الرقمية\" \"أ,ب,ج\" \"+966501234567\" \"باسم البسيمي\"")
        sys.exit(1)
    
    grade_name = sys.argv[1]
    subject_name = sys.argv[2]
    sections_str = sys.argv[3]
    phone_number = sys.argv[4]
    teacher_name = sys.argv[5] if len(sys.argv) > 5 else None
    
    sections = [s.strip() for s in sections_str.split(',')]
    
    # Credentials
    api_id = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH
    
    # اسم البوت و Token من settings
    bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    
    if bot_username:
        bot_username = bot_username.replace('@', '')  # إزالة @ إذا كان موجود
        print(f"[*] Bot @{bot_username} will be added to groups")
    
    if bot_token:
        print(f"[*] Bot token found - instructions will be sent from bot")
    
    print(f"[*] Creating {len(sections)} groups...\n")
    
    # تشغيل
    results = asyncio.run(create_groups(
        api_id, api_hash, phone_number, 
        grade_name, subject_name, sections,
        teacher_name=teacher_name,
        bot_username=bot_username,
        bot_token=bot_token
    ))
    
    # عرض ملخص
    success_count = sum(1 for r in results if r['success'])
    print(f"\n{'='*50}")
    print(f"[RESULT] Final result: {success_count}/{len(results)} succeeded")
    print(f"{'='*50}\n")
    
    # حفظ النتائج في ملف JSON
    output_file = 'telegram_groups_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"[SAVED] Results saved to: {output_file}")
    
    # تذكير بتطبيق الصلاحيات
    print(f"\n{'='*50}")
    print(f"[NEXT STEP] To apply read-only permissions:")
    print(f"python set_group_permissions.py")
    print(f"{'='*50}")
    
    # معلومات إضافية
    if success_count > 0:
        print(f"\n✅ البوت تمت إضافته وترقيته تلقائياً في جميع القروبات")
        print(f"✅ يمكنك الآن تطبيق صلاحيات read-only")
