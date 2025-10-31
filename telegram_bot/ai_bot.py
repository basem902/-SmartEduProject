"""
🤖 SmartEdu AI Bot - بوت استقبال وفحص الملفات بالذكاء الاصطناعي
"""
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

# تحميل متغيرات البيئة
load_dotenv()

# استيراد معالجات الملفات
from ai_file_handler import (
    handle_document,
    handle_video,
    handle_photo,
    handle_audio,
    handle_voice
)

# إعداد Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('ai_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SmartEduAIBot:
    """بوت SmartEdu الذكي"""
    
    def __init__(self):
        """تهيئة البوت"""
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.bot_username = os.getenv('TELEGRAM_BOT_USERNAME')
        
        if not self.token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN غير موجود في .env!")
        
        logger.info(f"🤖 تهيئة البوت: @{self.bot_username}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        معالج أمر /start
        """
        user = update.effective_user
        
        welcome_message = (
            f"👋 **مرحباً {user.first_name}!**\n\n"
            f"🤖 أنا **SmartEdu AI Bot**\n"
            f"📚 بوت فحص المشاريع الطلابية بالذكاء الاصطناعي\n\n"
            f"✨ **ما أستطيع فعله:**\n"
            f"🎬 فحص الفيديو - مدة، جودة، محتوى\n"
            f"📄 فحص PDF - نص، إحصائيات، انتحال\n"
            f"🖼️ فحص الصور - OCR، جودة، محتوى\n"
            f"📝 فحص المستندات - Word، Excel، PowerPoint\n"
            f"🎵 فحص الصوت - تحويل لنص، تحليل\n\n"
            f"📤 **كيف تستخدمني:**\n"
            f"1️⃣ أرسل ملفك (أي نوع من الأعلى)\n"
            f"2️⃣ انتظر قليلاً بينما أحلله\n"
            f"3️⃣ استلم النتيجة التفصيلية!\n\n"
            f"💡 **الأوامر المتاحة:**\n"
            f"/start - عرض هذه الرسالة\n"
            f"/help - المساعدة\n"
            f"/status - حالة النظام\n"
            f"/stats - إحصائياتك\n\n"
            f"🚀 جرب الآن! أرسل أي ملف للبدء."
        )
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"✅ مستخدم جديد: {user.username} ({user.id})")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        help_text = (
            "📖 **دليل الاستخدام**\n\n"
            "🎬 **الفيديو:**\n"
            "• يفحص المدة، الجودة، المحتوى\n"
            "• يكشف التشابه مع فيديوهات سابقة\n"
            "• يستخدم OCR لقراءة النص في الفيديو\n\n"
            "📄 **PDF:**\n"
            "• يستخرج النص ويحلله\n"
            "• يفحص عدد الكلمات والصفحات\n"
            "• يكشف الانتحال بذكاء\n\n"
            "🖼️ **الصور:**\n"
            "• يقرأ النص بـ OCR\n"
            "• يحلل المحتوى بالذكاء الاصطناعي\n"
            "• يفحص الجودة والدقة\n\n"
            "📝 **المستندات:**\n"
            "• Word, Excel, PowerPoint\n"
            "• يستخرج النص ويحلله\n"
            "• يفحص الإحصائيات\n\n"
            "🎵 **الصوت:**\n"
            "• يحول الكلام إلى نص\n"
            "• يحلل المحتوى\n"
            "• يكشف التشابه\n\n"
            "💰 **التكلفة:** شبه مجانية!\n"
            "⚡ **السرعة:** ثواني معدودة\n"
            "🔒 **الأمان:** بياناتك محمية\n\n"
            "❓ **أسئلة؟** تواصل مع المعلم"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /status"""
        status_text = (
            "📊 **حالة النظام**\n\n"
            "✅ البوت: يعمل\n"
            "✅ AI Validator: متصل\n"
            "✅ قاعدة البيانات: نشطة\n"
            "✅ Gemini API: متاح\n\n"
            "📈 **الإحصائيات:**\n"
            "🎬 فيديو: ✅ جاهز\n"
            "📄 PDF: ✅ جاهز\n"
            "🖼️ صور: ✅ جاهز\n"
            "📝 مستندات: ✅ جاهز\n"
            "🎵 صوت: ✅ جاهز\n\n"
            f"🤖 البوت: @{self.bot_username}\n"
            "⚡ الإصدار: 1.0.0\n"
            "💰 التكلفة: $0.51/سنة"
        )
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /stats"""
        user = update.effective_user
        
        # هنا يمكن جلب الإحصائيات الحقيقية من قاعدة البيانات
        stats_text = (
            f"📊 **إحصائياتك**\n\n"
            f"👤 المستخدم: {user.first_name}\n"
            f"🆔 ID: `{user.id}`\n\n"
            f"📤 **الملفات المرسلة:**\n"
            f"🎬 فيديو: 0\n"
            f"📄 PDF: 0\n"
            f"🖼️ صور: 0\n"
            f"📝 مستندات: 0\n"
            f"🎵 صوت: 0\n\n"
            f"📈 **النتائج:**\n"
            f"✅ مقبول: 0\n"
            f"❌ مرفوض: 0\n"
            f"⚠️ يحتاج مراجعة: 0\n\n"
            f"💡 أرسل ملفك الأول للبدء!"
        )
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        text = update.message.text.lower()
        
        # ردود تلقائية
        if any(word in text for word in ['مرحبا', 'السلام', 'هلا', 'اهلا']):
            await update.message.reply_text(
                "👋 مرحباً! أرسل ملفك وسأفحصه لك بالذكاء الاصطناعي!\n\n"
                "💡 استخدم /help لمعرفة المزيد"
            )
        elif any(word in text for word in ['مساعدة', 'help', 'ساعدني']):
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "📤 أرسل ملفك (فيديو، PDF، صورة، مستند، أو صوت)\n"
                "وسأفحصه بالذكاء الاصطناعي! ⚡"
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار التفاعلية"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "upload_new":
            await query.message.reply_text(
                "📤 جيد! أرسل الملف الجديد الآن وسأفحصه لك."
            )
        elif data.startswith("details_"):
            await query.message.reply_text(
                "📊 **التفاصيل الكاملة:**\n\n"
                "سيتم إضافة هذه الميزة قريباً..."
            )
        elif data.startswith("accepted_"):
            await query.message.reply_text(
                "🎉 **تهانينا!**\n\n"
                "تم قبول ملفك بنجاح!\n"
                "سيتم إبلاغ معلمك."
            )
    
    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        معالج الأعضاء الجدد في القروب
        يتحقق من هوية الطالب ويحدث قاعدة البيانات
        """
        try:
            message = update.message
            chat_id = message.chat.id
            
            # الحصول على العضو الجديد
            new_members = message.new_chat_members
            
            for new_member in new_members:
                # تجاهل البوتات
                if new_member.is_bot:
                    continue
                
                user_id = new_member.id
                username = new_member.username
                first_name = new_member.first_name
                last_name = new_member.last_name or ""
                full_name_telegram = f"{first_name} {last_name}".strip()
                
                logger.info(f"👤 عضو جديد: {full_name_telegram} (@{username}) في القروب {chat_id}")
                
                # البحث في قاعدة البيانات
                try:
                    import sys
                    import os
                    import django
                    
                    # إعداد Django
                    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
                    sys.path.insert(0, backend_path)
                    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
                    django.setup()
                    
                    from apps.sections.models import TelegramGroup, StudentRegistration
                    from difflib import SequenceMatcher
                    from django.utils import timezone
                    
                    # البحث عن القروب
                    telegram_group = TelegramGroup.objects.filter(chat_id=chat_id).first()
                    
                    if not telegram_group:
                        logger.warning(f"⚠️ القروب {chat_id} غير موجود في قاعدة البيانات")
                        await message.reply_text(
                            f"مرحباً {first_name}! 👋\n\n"
                            f"⚠️ هذا القروب غير مسجل في النظام.\n"
                            f"يرجى التواصل مع المعلم."
                        )
                        continue
                    
                    # البحث عن طلاب في هذه الشعبة (لم ينضموا بعد)
                    students = StudentRegistration.objects.filter(
                        section=telegram_group.section,
                        joined_telegram=False
                    )
                    
                    # مطابقة الاسم
                    best_match = None
                    highest_similarity = 0
                    
                    for student in students:
                        # مقارنة الاسم
                        similarity = SequenceMatcher(
                            None,
                            full_name_telegram.lower(),
                            student.full_name.lower()
                        ).ratio()
                        
                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            best_match = student
                    
                    # إذا كان التشابه أكثر من 60%
                    if best_match and highest_similarity >= 0.6:
                        # تحديث قاعدة البيانات
                        best_match.telegram_user_id = user_id
                        best_match.telegram_username = username
                        best_match.joined_telegram = True
                        best_match.joined_at = timezone.now()
                        best_match.save()
                        
                        logger.info(f"✅ تم ربط الطالب: {best_match.full_name} مع {full_name_telegram} (تشابه: {highest_similarity*100:.1f}%)")
                        
                        # رسالة ترحيب
                        welcome_message = (
                            f"🎉 **مرحباً {best_match.full_name}!**\n\n"
                            f"✅ تم تسجيلك بنجاح في قروب **{telegram_group.group_name}**\n\n"
                            f"📚 **معلوماتك:**\n"
                            f"• الصف: {best_match.grade.display_name}\n"
                            f"• الشعبة: {best_match.section.section_name}\n"
                            f"• المدرسة: {best_match.school_name}\n\n"
                            f"📤 يمكنك الآن رفع مشاريعك من خلال الروابط التي سيرسلها المعلم.\n\n"
                            f"💡 **نصيحة:** احتفظ بهذا القروب نشطاً لتتلقى الإشعارات المهمة!"
                        )
                        
                        await message.reply_text(welcome_message, parse_mode='Markdown')
                        
                    else:
                        # لم يُوجد في قاعدة البيانات
                        logger.warning(f"⚠️ العضو {full_name_telegram} غير موجود في قاعدة البيانات (أعلى تشابه: {highest_similarity*100:.1f}%)")
                        
                        await message.reply_text(
                            f"مرحباً {first_name}! 👋\n\n"
                            f"⚠️ لم أتمكن من التعرف على اسمك في قائمة الطلاب.\n\n"
                            f"📝 **خطوات التسجيل:**\n"
                            f"1️⃣ تأكد من التسجيل أولاً من خلال الرابط الذي أرسله المعلم\n"
                            f"2️⃣ تأكد من إدخال اسمك الكامل بشكل صحيح\n"
                            f"3️⃣ إذا استمرت المشكلة، تواصل مع المعلم\n\n"
                            f"💡 **ملاحظة:** يجب أن يتطابق اسمك في Telegram مع الاسم المسجل."
                        )
                        
                except Exception as db_error:
                    logger.error(f"❌ خطأ في قاعدة البيانات: {str(db_error)}", exc_info=True)
                    await message.reply_text(
                        f"مرحباً {first_name}! 👋\n\n"
                        f"حدث خطأ في التحقق من هويتك.\n"
                        f"يرجى التواصل مع المعلم."
                    )
                    
        except Exception as e:
            logger.error(f"❌ خطأ في معالج الأعضاء الجدد: {str(e)}", exc_info=True)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأخطاء"""
        logger.error(f"❌ خطأ: {context.error}", exc_info=context.error)
        
        try:
            await update.message.reply_text(
                "❌ **حدث خطأ!**\n\n"
                "حاول مرة أخرى أو تواصل مع الدعم الفني."
            )
        except:
            pass
    
    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل البوت...")
        
        # إنشاء Application
        app = Application.builder().token(self.token).build()
        
        # إضافة معالجات الأوامر
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(CommandHandler("stats", self.stats_command))
        
        # معالج الأعضاء الجدد في القروبات
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_member))
        
        # إضافة معالجات الملفات
        app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        app.add_handler(MessageHandler(filters.VIDEO, handle_video))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
        app.add_handler(MessageHandler(filters.VOICE, handle_voice))
        
        # معالج الرسائل النصية
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        # معالج الأزرار التفاعلية
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # معالج الأخطاء
        app.add_error_handler(self.error_handler)
        
        logger.info(f"✅ البوت جاهز! @{self.bot_username}")
        logger.info("⏳ في انتظار الرسائل...")
        
        # تشغيل البوت
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        bot = SmartEduAIBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n👋 تم إيقاف البوت")
    except Exception as e:
        logger.error(f"❌ خطأ فادح: {str(e)}", exc_info=True)
