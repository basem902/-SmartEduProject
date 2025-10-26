"""
إنشاء وإدارة مجموعات Telegram باستخدام Telethon
نسخة محسّنة ومدمجة مع Django
"""
import asyncio
import os
import sys
import json
import django

# إعداد Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from telethon import TelegramClient, functions, types, errors


async def ensure_authorized(client: TelegramClient, phone: str) -> None:
    """يتأكد من تسجيل الدخول - للـ subprocess يجب أن تكون الجلسة موجودة مسبقاً."""
    print(f"DEBUG: Connecting to Telegram for phone: {phone}")
    await client.connect()
    print(f"DEBUG: Connected! Checking authorization...")
    
    is_authorized = await client.is_user_authorized()
    print(f"DEBUG: is_user_authorized = {is_authorized}")
    
    if is_authorized:
        print("✓ الجلسة مخوّلة مسبقًا")
        return
    
    # في subprocess لا يمكننا طلب input من المستخدم
    print("ERROR: User is NOT authorized!")
    print(f"ERROR: Phone: {phone}")
    print(f"ERROR: Session path should be: backend/sessions/session_{phone.replace('+', '')}.session")
    
    raise RuntimeError(
        "❌ الجلسة غير موجودة أو منتهية!\n"
        "يرجى تسجيل الدخول أولاً من صفحة الاختبار (زر 'ربط حساب Telegram')"
    )


async def create_group(client: TelegramClient, title: str, about: str):
    """ينشئ سوبرقروب ويعيد كائن القناة."""
    res = await client(functions.channels.CreateChannelRequest(
        title=title,
        about=about,
        megagroup=True
    ))
    channel = res.chats[0]
    print(f"✓ تم إنشاء القروب: {title}")
    return channel


async def show_history_for_new_joiners(client: TelegramClient, channel):
    """يُظهر السجل للمنضمين الجدد."""
    try:
        await client(functions.channels.TogglePreHistoryHiddenRequest(
            channel=channel, 
            enabled=False
        ))
        print("✓ تم تفعيل السجل للمنضمين الجدد")
    except errors.ChatNotModifiedError:
        print("✓ السجل مفعل بالفعل")


async def send_and_pin_instructions(client: TelegramClient, channel, text: str):
    """يرسل رسالة التعليمات ويثبتها."""
    msg = await client.send_message(channel, text)
    try:
        await client(functions.messages.UpdatePinnedMessageRequest(
            peer=channel, 
            id=msg.id, 
            silent=True
        ))
        print("✓ تم تثبيت التعليمات")
    except Exception as e:
        print(f"⚠ خطأ في تثبيت الرسالة: {e}")
    return msg


async def set_readonly_for_members(client: TelegramClient, channel):
    """يضبط صلاحيات القراءة فقط للأعضاء."""
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
    print("✓ تم تفعيل وضع القراءة فقط")


async def invite_bot(client: TelegramClient, channel, bot_username: str):
    """يدعو البوت إلى القروب."""
    try:
        await client(functions.channels.InviteToChannelRequest(
            channel=channel,
            users=[bot_username]
        ))
        print(f"✓ تمت دعوة البوت: {bot_username}")
        await asyncio.sleep(3)  # انتظار لتسجيل الانضمام
    except errors.UserAlreadyParticipantError:
        print("✓ البوت موجود بالفعل")


async def promote_bot_with_retry(client: TelegramClient, channel, bot_username: str):
    """يرقي البوت كمشرف مع retry logic."""
    # محاولة 1: صلاحيات كاملة
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
    
    try:
        await client(functions.channels.EditAdminRequest(
            channel=channel,
            user_id=bot_username,
            admin_rights=full_rights,
            rank="Bot"
        ))
        print("✓ تمت ترقية البوت (صلاحيات كاملة)")
        return True
    except Exception as e:
        print(f"⚠ فشلت الترقية الكاملة: {e}")
    
    # محاولة 2: صلاحيات أساسية
    await asyncio.sleep(2)
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
    
    try:
        await client(functions.channels.EditAdminRequest(
            channel=channel,
            user_id=bot_username,
            admin_rights=minimal_rights,
            rank="Bot"
        ))
        print("✓ تمت ترقية البوت (صلاحيات أساسية)")
        return True
    except Exception as e:
        print(f"❌ فشلت ترقية البوت: {e}")
        return False


async def export_invite_link(client: TelegramClient, channel) -> str:
    """يستخرج رابط الدعوة."""
    invite = await client(functions.messages.ExportChatInviteRequest(peer=channel))
    return invite.link


async def create_class_groups(api_id, api_hash, phone_number, grade_name, subject_name, sections, school_name=None, teacher_name=None, bot_username=None, bot_token=None):
    """
    إنشاء القروبات باستخدام Telethon
    
    Args:
        api_id: Telegram API ID
        api_hash: Telegram API Hash
        phone_number: رقم الهاتف
        grade_name: اسم الصف
        subject_name: اسم المادة
        sections: قائمة الشُعب
        school_name: اسم المدرسة (اختياري)
        bot_username: اسم البوت بدون @ (اختياري)
        bot_token: Bot token (غير مستخدم في Telethon)
    
    Returns:
        قائمة بالنتائج
    """
    # اسم الجلسة
    session_name = f"session_{phone_number.replace('+', '')}"
    sessions_dir = os.path.join(settings.BASE_DIR, 'sessions')
    os.makedirs(sessions_dir, exist_ok=True)
    session_path = os.path.join(sessions_dir, session_name)
    
    print(f"DEBUG: Session name: {session_name}")
    print(f"DEBUG: Sessions dir: {sessions_dir}")
    print(f"DEBUG: Full session path: {session_path}")
    print(f"DEBUG: Session file exists: {os.path.exists(f'{session_path}.session')}")
    
    # إنشاء Client
    client = TelegramClient(session_path, api_id, api_hash)
    
    results = []
    
    try:
        # التأكد من تسجيل الدخول
        await ensure_authorized(client, phone_number)
        
        print("\n" + "=" * 60)
        print(f"بدء إنشاء القروبات للصف: {grade_name}")
        print(f"عدد الشُعب: {len(sections)}")
        print("=" * 60 + "\n")
        
        for i, section in enumerate(sections, 1):
            print(f"\n[{i}/{len(sections)}] معالجة الشعبة: {section}")
            print("-" * 40)
            
            # اسم القروب
            if school_name:
                group_name = f"{subject_name} | {grade_name} | شعبة {section} | {school_name}"
            else:
                group_name = f"{subject_name} | {grade_name} | شعبة {section}"
            
            about = f"منصتك الشاملة للتميز الأكاديمي — مشاريع، إحصائيات، ملفات، تنبيهات"
            instructions = f"""
╔══════════════════════╗
║  🎓 مرحباً بكم! 🎓  ║
╚══════════════════════╝

📚 **المادة:** {subject_name}
🏫 **الصف:** {grade_name} - الشعبة {section}
👨‍🏫 **المعلم:** {'أ. ' + teacher_name if teacher_name and not teacher_name.startswith('أ.') else (teacher_name or '[سيتم التحديث]')}

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
            
            try:
                # 1. إنشاء القروب
                channel = await create_group(client, group_name, about)
                await asyncio.sleep(2)
                
                # 2. إظهار السجل
                await show_history_for_new_joiners(client, channel)
                await asyncio.sleep(1)
                
                # 3. إرسال وتثبيت التعليمات
                msg = await send_and_pin_instructions(client, channel, instructions)
                await asyncio.sleep(2)
                
                # 4. تطبيق القراءة فقط
                await set_readonly_for_members(client, channel)
                await asyncio.sleep(2)
                
                # 5. إضافة البوت (إذا تم تحديده)
                if bot_username:
                    bot_user = bot_username if bot_username.startswith('@') else f'@{bot_username}'
                    await invite_bot(client, channel, bot_user)
                    await asyncio.sleep(3)
                    
                    # 6. ترقية البوت
                    bot_promoted = await promote_bot_with_retry(client, channel, bot_user)
                    if not bot_promoted:
                        print("⚠ تحذير: فشلت ترقية البوت")
                
                # 7. استخراج رابط الدعوة
                invite_link = await export_invite_link(client, channel)
                
                print(f"\n✅ نجح إنشاء القروب:")
                print(f"   Chat ID: {channel.id}")
                print(f"   Link: {invite_link}")
                
                results.append({
                    'success': True,
                    'section_name': section,
                    'group_name': group_name,
                    'chat_id': channel.id,
                    'invite_link': invite_link,
                    'message_id': msg.id if msg else None
                })
                
                # تأخير بين القروبات
                if i < len(sections):
                    print(f"\n⏳ انتظار 30 ثانية قبل القروب التالي...")
                    await asyncio.sleep(30)
                
            except errors.FloodWaitError as e:
                print(f"❌ FloodWait: يجب الانتظار {e.seconds} ثانية")
                results.append({
                    'success': False,
                    'section_name': section,
                    'group_name': group_name,
                    'error': f'FloodWait: {e.seconds} seconds'
                })
                
            except Exception as e:
                print(f"❌ خطأ في إنشاء القروب: {e}")
                results.append({
                    'success': False,
                    'section_name': section,
                    'group_name': group_name,
                    'error': str(e)
                })
        
        print("\n" + "=" * 60)
        print("✅ اكتملت عملية الإنشاء")
        success_count = sum(1 for r in results if r['success'])
        print(f"النجاح: {success_count}/{len(sections)}")
        print("=" * 60 + "\n")
        
        # حفظ النتائج في ملف JSON للـ Django backend
        results_file = os.path.join(settings.BASE_DIR, 'telegram_groups_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✓ تم حفظ النتائج في: {results_file}")
        
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()
    
    return results


# للاختبار المباشر
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 7:
        print("Usage: python create_groups_telethon.py <phone> <grade> <subject> <school> <teacher_name> <sections...>")
        print("Example: python create_groups_telethon.py +966558048004 'الثاني متوسط' 'المهارات الرقمية' 'مدرسة النور' 'أ. محمد' 1 2 3")
        sys.exit(1)
    
    phone = sys.argv[1]
    grade = sys.argv[2]
    subject = sys.argv[3]
    school = sys.argv[4]
    teacher = sys.argv[5]
    sections = sys.argv[6:]
    
    results = asyncio.run(create_class_groups(
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        phone_number=phone,
        grade_name=grade,
        subject_name=subject,
        sections=sections,
        school_name=school,
        teacher_name=teacher,
        bot_username=settings.TELEGRAM_BOT_USERNAME
    ))
    
    print("\n📊 النتائج النهائية:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} الشعبة {r['section_name']}: {r.get('invite_link', r.get('error', 'Unknown'))}")
