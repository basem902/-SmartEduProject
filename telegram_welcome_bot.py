"""
Telegram Bot للترحيب بالطلاب وتحديث Database
يعمل عندما ينضم طالب جديد لأي قروب
"""

import os
import sys
import logging
import asyncio
import requests
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


def main():
    """
    تشغيل البوت
    """
    try:
        # إنشاء Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة Handler للأعضاء الجدد
        application.add_handler(
            ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER)
        )
        
        logger.info("🤖 Bot بدأ العمل...")
        logger.info(f"📡 API URL: {API_BASE_URL}")
        logger.info("👂 في انتظار انضمام الطلاب...")
        
        # بدء البوت
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {str(e)}", exc_info=True)


if __name__ == '__main__':
    main()
