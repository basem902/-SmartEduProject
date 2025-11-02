"""
Telegram Bot للترحيب بالطلاب وتحديث Database
يعمل عندما ينضم طالب جديد لأي قروب
"""

import os
import sys
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# إعداد المسارات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from apps.sections.models import StudentRegistration, TelegramGroup

# إعداد Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# البيانات من .env
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8454359902:AAF-yYkwNnjbtg1O0juwxcOBXy4MlhnU4nU')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')


async def bot_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    يُستدعى عندما يُضاف البوت نفسه لمجموعة جديدة
    """
    try:
        chat_member_update = update.my_chat_member
        
        if not chat_member_update:
            return
        
        new_status = chat_member_update.new_chat_member.status
        old_status = chat_member_update.old_chat_member.status
        chat = update.effective_chat
        
        # التحقق من أن البوت تمت إضافته للتو
        if old_status in ['left', 'kicked'] and new_status in ['member', 'administrator', 'creator']:
            logger.info(f"🤖 Bot added to group: {chat.title} (ID: {chat.id})")
            
            # التحقق من الصلاحيات
            bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
            is_admin = bot_member.status in ['administrator', 'creator']
            
            if is_admin:
                # البوت مشرف - رائع!
                welcome_msg = f"""
✅ **تم إضافتي بنجاح!**

مرحباً! أنا **SmartEdu Bot** 🤖

✅ **حالتي:** مشرف في المجموعة  
📱 **الوظائف:**
• الترحيب بالطلاب الجدد
• تحديث قاعدة البيانات تلقائياً
• إدارة الأعضاء

🎉 **جاهز للعمل!**
"""
                logger.info(f"✅ Bot is already admin in {chat.title}")
                
            else:
                # البوت ليس مشرف - رسالة تذكيرية
                welcome_msg = f"""
⚠️ **تم إضافتي للمجموعة!**

مرحباً! أنا **SmartEdu Bot** 🤖

❗ **لكي أعمل بشكل كامل، يرجى ترقيتي لمشرف:**

📝 **الخطوات:**
1️⃣ اضغط على اسم المجموعة أعلى الشاشة
2️⃣ اختر **Administrators** (المشرفون)
3️⃣ اضغط **Add Admin** (إضافة مشرف)
4️⃣ ابحث عن: **SmartEduProjectsBot**
5️⃣ فعّل الصلاحيات التالية:
   ✅ Delete messages (حذف الرسائل)
   ✅ Invite users (إضافة أعضاء)
   ✅ Pin messages (تثبيت رسائل)
   ✅ Manage chat (إدارة الدردشة)

⏳ **بعد الترقية سأعمل تلقائياً!**

💡 أو يمكنك استخدام زر "ترقية البوت" من لوحة التحكم في الموقع.
"""
                logger.warning(f"⚠️ Bot is NOT admin in {chat.title}")
            
            # إرسال الرسالة
            await context.bot.send_message(
                chat_id=chat.id,
                text=welcome_msg,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Sent welcome message to {chat.title}")
            
    except Exception as e:
        logger.error(f"❌ Error in bot_added_to_group: {str(e)}", exc_info=True)


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    يُستدعى عندما ينضم عضو جديد للقروب
    """
    try:
        # الحصول على معلومات العضو الجديد
        chat_member_update = update.chat_member
        
        # التحقق من أنه انضمام جديد وليس مغادرة
        if chat_member_update.new_chat_member.status not in ['member', 'administrator', 'creator']:
            return
        
        if chat_member_update.old_chat_member.status in ['member', 'administrator', 'creator']:
            return
        
        # معلومات العضو الجديد
        new_member = chat_member_update.new_chat_member.user
        chat = update.effective_chat
        
        user_id = new_member.id
        username = new_member.username or ''
        first_name = new_member.first_name or 'الطالب'
        chat_id = chat.id
        
        logger.info(f"👤 عضو جديد انضم: {first_name} (@{username}, ID: {user_id}) في القروب {chat_id}")
        
        # 1️⃣ البحث عن القروب في Database
        try:
            telegram_group = TelegramGroup.objects.get(chat_id=chat_id)
            section = telegram_group.section
            
            logger.info(f"📚 القروب: {telegram_group.group_name} - الشعبة: {section.section_name}")
            
        except TelegramGroup.DoesNotExist:
            logger.warning(f"⚠️  القروب {chat_id} غير موجود في Database")
            # إرسال رسالة ترحيب عامة
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🎉 مرحباً {first_name}!\n\n"
                     f"أهلاً بك في القروب التعليمي 📚"
            )
            return
        
        # 2️⃣ البحث عن الطالب في Database
        # نبحث عن طالب في هذه الشعبة لم ينضم بعد للتليجرام
        students = StudentRegistration.objects.filter(
            section=section,
            joined_telegram=False
        ).order_by('-registered_at')
        
        matched_student = None
        
        # محاولة المطابقة بالـ telegram_user_id إذا كان محفوظاً مسبقاً
        for student in students:
            if student.telegram_user_id == user_id:
                matched_student = student
                break
        
        # إذا لم نجد، نفترض أول طالب غير منضم
        if not matched_student and students.exists():
            matched_student = students.first()
            logger.info(f"💡 افتراض أن الطالب هو: {matched_student.full_name}")
        
        # 3️⃣ تحديث Database
        if matched_student:
            # استدعاء API لتحديث البيانات
            api_url = f"{API_BASE_URL}/sections/confirm-student-joined/"
            payload = {
                'student_id': matched_student.id,
                'telegram_user_id': user_id,
                'telegram_username': username,
                'chat_id': chat_id
            }
            
            try:
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ تم تحديث Database للطالب: {matched_student.full_name}")
                    student_name = matched_student.full_name
                else:
                    logger.error(f"❌ فشل تحديث Database: {response.text}")
                    student_name = first_name
            except Exception as e:
                logger.error(f"❌ خطأ في استدعاء API: {str(e)}")
                student_name = first_name
        else:
            logger.warning(f"⚠️  لم نجد طالب مطابق في Database")
            student_name = first_name
        
        # 4️⃣ إرسال رسالة ترحيب
        welcome_message = f"""
🎉 **مرحباً {student_name}!**

أهلاً بك في قروب **{telegram_group.group_name}** 📚

━━━━━━━━━━━━━━━━━━━━

📖 **معلومات الشعبة:**
🏫 المدرسة: {section.grade.school_name}
📚 الصف: {section.grade.display_name}
📖 الشعبة: {section.section_name}

━━━━━━━━━━━━━━━━━━━━

💡 **ملاحظات مهمة:**
• تأكد من قراءة قوانين القروب
• سيتم نشر المشاريع والواجبات هنا
• يمكنك التواصل مع المعلم عند الحاجة

نتمنى لك تجربة تعليمية ممتعة! 🎓✨
"""
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ تم إرسال رسالة الترحيب ل {student_name}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في welcome_new_member: {str(e)}", exc_info=True)


async def periodic_admin_check(context: ContextTypes.DEFAULT_TYPE):
    """
    فحص دوري للتأكد من أن البوت مشرف في جميع المجموعات
    يعمل كل ساعة
    """
    try:
        logger.info("🔍 بدء الفحص الدوري لصلاحيات البوت...")
        
        # جلب جميع المجموعات من Database
        telegram_groups = TelegramGroup.objects.filter(is_active=True)
        
        if not telegram_groups.exists():
            logger.info("ℹ️ لا توجد مجموعات في Database")
            return
        
        checked = 0
        is_admin = 0
        not_admin = 0
        errors = 0
        
        for group in telegram_groups:
            try:
                checked += 1
                
                # التحقق من صلاحيات البوت
                bot_member = await context.bot.get_chat_member(group.chat_id, context.bot.id)
                
                if bot_member.status in ['administrator', 'creator']:
                    is_admin += 1
                    logger.debug(f"✅ البوت مشرف في: {group.group_name}")
                else:
                    not_admin += 1
                    logger.warning(f"⚠️ البوت ليس مشرف في: {group.group_name}")
                    
                    # إرسال تذكير (اختياري - مرة واحدة فقط)
                    try:
                        reminder_msg = f"""
⚠️ **تذكير: يرجى ترقية البوت**

أنا البوت **SmartEdu Bot** 🤖

❗ لست مشرفاً في هذه المجموعة حالياً.

💡 **لكي أعمل بشكل كامل:**
   → اذهب لإعدادات المجموعة
   → اضغط Administrators
   → اضغط Add Admin
   → ابحث عن: SmartEduProjectsBot
   → منحني الصلاحيات

🔧 أو استخدم زر "ترقية البوت" من لوحة التحكم.

شكراً! 🙏
"""
                        await context.bot.send_message(
                            chat_id=group.chat_id,
                            text=reminder_msg,
                            parse_mode='Markdown'
                        )
                        logger.info(f"📧 تم إرسال تذكير لـ: {group.group_name}")
                    except Exception as e:
                        logger.debug(f"لم يتم إرسال التذكير: {e}")
                
                # تأخير صغير لتجنب Flood
                await asyncio.sleep(1)
                
            except Exception as e:
                errors += 1
                logger.error(f"❌ خطأ في فحص {group.group_name}: {e}")
        
        # ملخص الفحص
        logger.info("=" * 60)
        logger.info(f"📊 ملخص الفحص الدوري:")
        logger.info(f"   ✅ مجموعات تم فحصها: {checked}")
        logger.info(f"   👑 البوت مشرف في: {is_admin}")
        logger.info(f"   ⚠️  البوت ليس مشرف في: {not_admin}")
        logger.info(f"   ❌ أخطاء: {errors}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ خطأ في periodic_admin_check: {str(e)}", exc_info=True)


def main():
    """
    تشغيل البوت
    """
    try:
        # إنشاء Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Handler 1: عند إضافة البوت لمجموعة جديدة
        application.add_handler(
            ChatMemberHandler(bot_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER)
        )
        
        # Handler 2: عند انضمام أعضاء جدد (الطلاب)
        application.add_handler(
            ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER)
        )
        
        # الفحص الدوري: كل ساعة (اختياري - يحتاج job-queue)
        job_queue = application.job_queue
        if job_queue:
            job_queue.run_repeating(
                periodic_admin_check,
                interval=3600,  # كل ساعة (بالثواني)
                first=60  # الفحص الأول بعد دقيقة من التشغيل
            )
            logger.info("🤖 Bot بدأ العمل...")
            logger.info(f"📡 API URL: {API_BASE_URL}")
            logger.info("👂 في انتظار:")
            logger.info("   • إضافة البوت لمجموعات جديدة")
            logger.info("   • انضمام الطلاب")
            logger.info("   • فحص دوري كل ساعة ✅")
        else:
            logger.warning("⚠️ JobQueue غير متاح - الفحص الدوري معطل")
            logger.warning("💡 لتفعيله: pip install python-telegram-bot[job-queue]")
            logger.info("🤖 Bot بدأ العمل...")
            logger.info(f"📡 API URL: {API_BASE_URL}")
            logger.info("👂 في انتظار:")
            logger.info("   • إضافة البوت لمجموعات جديدة")
            logger.info("   • انضمام الطلاب")
        
        # بدء البوت
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {str(e)}", exc_info=True)


if __name__ == '__main__':
    main()
