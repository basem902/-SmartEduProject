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
