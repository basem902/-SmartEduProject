"""
🤖 معالج الملفات الذكي - Telegram Bot AI Handler
يستقبل الملفات من تليجرام ويحللها بالذكاء الاصطناعي
"""
import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class AIFileHandler:
    """معالج الملفات بالذكاء الاصطناعي"""
    
    # أنواع الملفات المدعومة
    SUPPORTED_TYPES = {
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'],
        'pdf': ['.pdf'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'document': ['.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
    }
    
    def __init__(self, api_base_url='http://localhost:8000/api'):
        """
        تهيئة معالج الملفات
        
        Args:
            api_base_url: رابط الـ API
        """
        self.api_base_url = api_base_url
        self.downloads_dir = Path('downloads')
        self.downloads_dir.mkdir(exist_ok=True)
    
    def get_file_type(self, filename):
        """
        تحديد نوع الملف
        
        Args:
            filename: اسم الملف
            
        Returns:
            str: نوع الملف أو None
        """
        ext = Path(filename).suffix.lower()
        
        for file_type, extensions in self.SUPPORTED_TYPES.items():
            if ext in extensions:
                return file_type
        
        return None
    
    def format_size(self, size_bytes):
        """
        تنسيق حجم الملف
        
        Args:
            size_bytes: الحجم بالبايت
            
        Returns:
            str: الحجم منسق
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        معالجة الملف المستلم
        
        Args:
            update: تحديث تليجرام
            context: سياق البوت
        """
        user = update.effective_user
        message = update.message
        
        # تحديد نوع الملف
        file_obj = None
        filename = None
        file_size = 0
        
        if message.document:
            file_obj = message.document
            filename = file_obj.file_name
            file_size = file_obj.file_size
        elif message.video:
            file_obj = message.video
            filename = f"video_{user.id}_{int(datetime.now().timestamp())}.mp4"
            file_size = file_obj.file_size
        elif message.photo:
            file_obj = message.photo[-1]  # أكبر حجم
            filename = f"photo_{user.id}_{int(datetime.now().timestamp())}.jpg"
            file_size = file_obj.file_size
        elif message.audio:
            file_obj = message.audio
            filename = file_obj.file_name or f"audio_{user.id}_{int(datetime.now().timestamp())}.mp3"
            file_size = file_obj.file_size
        elif message.voice:
            file_obj = message.voice
            filename = f"voice_{user.id}_{int(datetime.now().timestamp())}.ogg"
            file_size = file_obj.file_size
        
        if not file_obj:
            await message.reply_text("❌ لم أتمكن من التعرف على الملف!")
            return
        
        logger.info(f"📥 ملف جديد من {user.username}: {filename} ({self.format_size(file_size)})")
        
        # التحقق من نوع الملف
        file_type = self.get_file_type(filename)
        
        if not file_type:
            await message.reply_text(
                "❌ **نوع ملف غير مدعوم!**\n\n"
                "✅ الأنواع المدعومة:\n"
                "🎬 فيديو: MP4, AVI, MOV\n"
                "📄 PDF: PDF\n"
                "🖼️ صور: JPG, PNG, GIF\n"
                "📝 مستندات: DOCX, XLSX, PPTX\n"
                "🎵 صوت: MP3, WAV, OGG",
                parse_mode='Markdown'
            )
            return
        
        # رسالة معالجة
        processing_msg = await message.reply_text(
            f"⏳ **جاري معالجة الملف...**\n\n"
            f"📁 الملف: `{filename}`\n"
            f"📊 الحجم: {self.format_size(file_size)}\n"
            f"🔍 النوع: {self._get_type_emoji(file_type)} {file_type}\n\n"
            f"⚡ يتم الآن:\n"
            f"1️⃣ تحميل الملف...",
            parse_mode='Markdown'
        )
        
        try:
            # تحميل الملف
            file = await context.bot.get_file(file_obj.file_id)
            file_path = self.downloads_dir / filename
            await file.download_to_drive(file_path)
            
            logger.info(f"✅ تم تحميل: {file_path}")
            
            # تحديث الرسالة
            await processing_msg.edit_text(
                f"⏳ **جاري معالجة الملف...**\n\n"
                f"📁 الملف: `{filename}`\n"
                f"📊 الحجم: {self.format_size(file_size)}\n"
                f"🔍 النوع: {self._get_type_emoji(file_type)} {file_type}\n\n"
                f"⚡ يتم الآن:\n"
                f"✅ تم التحميل\n"
                f"2️⃣ فحص بالذكاء الاصطناعي...",
                parse_mode='Markdown'
            )
            
            # استدعاء AI Validator
            result = await self._validate_with_ai(file_path, file_type, user.id)
            
            # حذف الملف بعد المعالجة
            if file_path.exists():
                file_path.unlink()
            
            # عرض النتائج
            await self._send_results(message, processing_msg, result, filename, file_type)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الملف: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ **حدث خطأ في المعالجة!**\n\n"
                f"الخطأ: `{str(e)}`\n\n"
                f"💡 حاول مرة أخرى أو تواصل مع المعلم.",
                parse_mode='Markdown'
            )
    
    async def _validate_with_ai(self, file_path, file_type, user_id):
        """
        التحقق من الملف باستخدام AI
        
        Args:
            file_path: مسار الملف
            file_type: نوع الملف
            user_id: معرف المستخدم
            
        Returns:
            dict: نتيجة التحقق
        """
        # هنا يتم استدعاء AI Validator من Django
        # سأضيف integration كامل لاحقاً
        
        # محاكاة للاختبار
        await asyncio.sleep(2)  # محاكاة وقت المعالجة
        
        return {
            'status': 'approved',
            'overall_score': 85.5,
            'checks': {
                'quality': {'status': 'pass', 'message': 'جودة ممتازة', 'score': 90},
                'content': {'status': 'pass', 'message': 'محتوى مناسب', 'score': 85},
                'plagiarism': {'status': 'pass', 'message': 'لا يوجد تشابه', 'score': 100}
            },
            'warnings': [],
            'rejection_reasons': []
        }
    
    async def _send_results(self, message, processing_msg, result, filename, file_type):
        """
        إرسال نتائج الفحص
        
        Args:
            message: رسالة تليجرام الأصلية
            processing_msg: رسالة المعالجة
            result: نتيجة الفحص
            filename: اسم الملف
            file_type: نوع الملف
        """
        status = result['status']
        score = result['overall_score']
        
        # Emoji حسب الحالة
        status_emoji = {
            'approved': '✅',
            'rejected': '❌',
            'needs_review': '⚠️'
        }.get(status, '❓')
        
        status_text = {
            'approved': 'مقبول',
            'rejected': 'مرفوض',
            'needs_review': 'يحتاج مراجعة'
        }.get(status, 'غير معروف')
        
        # بناء الرسالة
        result_text = f"{status_emoji} **النتيجة: {status_text}**\n\n"
        result_text += f"📁 الملف: `{filename}`\n"
        result_text += f"🔍 النوع: {self._get_type_emoji(file_type)} {file_type}\n"
        result_text += f"📊 الدرجة: **{score:.1f}%**\n\n"
        
        result_text += "🔬 **تفاصيل الفحص:**\n"
        
        # الفحوصات
        for check_name, check_data in result.get('checks', {}).items():
            check_status = check_data.get('status', 'unknown')
            check_emoji = '✅' if check_status == 'pass' else '⚠️' if check_status == 'warning' else '❌'
            check_msg = check_data.get('message', 'N/A')
            check_score = check_data.get('score', 0)
            
            result_text += f"{check_emoji} {check_name}: {check_msg} ({check_score}%)\n"
        
        # التحذيرات
        if result.get('warnings'):
            result_text += "\n⚠️ **تحذيرات:**\n"
            for warning in result['warnings']:
                result_text += f"• {warning}\n"
        
        # أسباب الرفض
        if result.get('rejection_reasons'):
            result_text += "\n❌ **أسباب الرفض:**\n"
            for reason in result['rejection_reasons']:
                result_text += f"• {reason}\n"
        
        result_text += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # أزرار تفاعلية
        keyboard = []
        
        if status == 'approved':
            keyboard.append([InlineKeyboardButton("🎉 تم القبول", callback_data=f"accepted_{filename}")])
        elif status == 'rejected':
            keyboard.append([InlineKeyboardButton("🔄 رفع ملف جديد", callback_data="upload_new")])
        
        keyboard.append([InlineKeyboardButton("📊 عرض التفاصيل الكاملة", callback_data=f"details_{filename}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # إرسال النتيجة
        await processing_msg.edit_text(result_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    def _get_type_emoji(self, file_type):
        """
        الحصول على emoji حسب نوع الملف
        
        Args:
            file_type: نوع الملف
            
        Returns:
            str: emoji
        """
        return {
            'video': '🎬',
            'pdf': '📄',
            'image': '🖼️',
            'document': '📝',
            'audio': '🎵'
        }.get(file_type, '📁')


# Handler functions للاستخدام مع البوت
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج المستندات"""
    handler = AIFileHandler()
    await handler.handle_file(update, context)


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الفيديو"""
    handler = AIFileHandler()
    await handler.handle_file(update, context)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الصور"""
    handler = AIFileHandler()
    await handler.handle_file(update, context)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الصوت"""
    handler = AIFileHandler()
    await handler.handle_file(update, context)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل الصوتية"""
    handler = AIFileHandler()
    await handler.handle_file(update, context)
