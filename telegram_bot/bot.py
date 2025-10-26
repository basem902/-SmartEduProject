"""
Telegram Bot Main Application
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import BotConfig
from utils import TelegramHelper, MessageFormatter, DatabaseHelper

# إعداد Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, BotConfig.LOG_LEVEL),
    handlers=[
        logging.FileHandler(BotConfig.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class OTPBot:
    """بوت رموز OTP"""
    
    def __init__(self):
        self.db = DatabaseHelper()
        self.db.connect()
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        معالج أمر /start
        
        عندما يضغط الطالب على الرابط من الموقع، يصل هنا
        Format: /start <signed_otp_id>
        """
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        logger.info(f"Start command from {user.id} (@{user.username})")
        
        # التحقق من وجود معامل
        if not context.args:
            await update.message.reply_text(
                MessageFormatter.welcome_message("الطالب"),
                parse_mode='Markdown'
            )
            return
        
        # استخراج OTP ID
        signed_otp_id = context.args[0]
        otp_id = TelegramHelper.verify_signature(signed_otp_id, BotConfig.SECRET_KEY)
        
        if not otp_id:
            logger.warning(f"Invalid signature: {signed_otp_id}")
            await update.message.reply_text(
                MessageFormatter.error_message('invalid_link'),
                parse_mode='Markdown'
            )
            return
        
        # جلب بيانات OTP
        otp_data = self.db.get_otp_record(otp_id)
        
        if not otp_data:
            logger.error(f"OTP not found: {otp_id}")
            await update.message.reply_text(
                MessageFormatter.error_message('invalid_link'),
                parse_mode='Markdown'
            )
            return
        
        # التحقق من الحالة
        if otp_data['status'] == 'used':
            await update.message.reply_text(
                MessageFormatter.error_message('already_used'),
                parse_mode='Markdown'
            )
            return
        
        # التحقق من العضوية في القروب
        telegram_link = otp_data['telegram_link']
        if not telegram_link:
            logger.error(f"No telegram link for section {otp_data['section_id']}")
            await update.message.reply_text(
                MessageFormatter.error_message('general'),
                parse_mode='Markdown'
            )
            return
        
        # استخراج معرّف القروب
        group_id = TelegramHelper.extract_group_id(telegram_link)
        
        if not group_id:
            logger.error(f"Cannot extract group_id from: {telegram_link}")
            await update.message.reply_text(
                MessageFormatter.error_message('general'),
                parse_mode='Markdown'
            )
            return
        
        # التحقق من العضوية
        is_member = await self.check_membership(context, group_id, user.id)
        
        if not is_member:
            logger.info(f"User {user.id} is not a member of {group_id}")
            await update.message.reply_text(
                MessageFormatter.not_member_message(telegram_link),
                parse_mode='Markdown'
            )
            
            # تسجيل الحدث
            self.db.create_log(otp_id, 'sent', 'غير عضو في القروب')
            return
        
        # الطالب عضو! حفظ بياناته وإرسال الكود
        self.db.update_otp_telegram_info(
            otp_id,
            user.id,
            chat_id,
            user.username
        )
        
        # إرسال الكود
        message = MessageFormatter.send_otp_code(
            otp_data['student_name'],
            otp_data['code'],
            expires_minutes=10
        )
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        # تسجيل الحدث
        self.db.create_log(otp_id, 'sent', f'تم إرسال الكود للمستخدم {user.id}')
        
        logger.info(f"Code sent to user {user.id} for OTP {otp_id}")
    
    async def check_membership(self, context: ContextTypes.DEFAULT_TYPE, group_id: str, user_id: int):
        """
        التحقق من عضوية المستخدم في القروب
        
        Args:
            context: Bot context
            group_id: معرّف القروب (username أو chat_id)
            user_id: معرّف المستخدم
            
        Returns:
            bool: True إذا كان عضواً
        """
        try:
            # إذا كان group_id يبدأ بـ @ فهو username
            if group_id.startswith('@'):
                chat_id = group_id
            else:
                # إذا كان join link، نحتاج لمعالجة خاصة
                # لكن getChatMember يتطلب chat_id أو @username
                chat_id = f"@{group_id}" if not group_id.startswith('@') else group_id
            
            member = await context.bot.get_chat_member(chat_id, user_id)
            
            # التحقق من حالة العضوية
            return member.status in ['member', 'administrator', 'creator']
            
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            # في حالة الخطأ، نفترض أنه ليس عضواً
            return False
    
    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        await update.message.reply_text(
            MessageFormatter.help_message(),
            parse_mode='Markdown'
        )
    
    async def unknown_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل غير المعروفة"""
        await update.message.reply_text(
            "عذراً، لم أفهم هذا الأمر.\nاستخدم /help للمساعدة.",
            parse_mode='Markdown'
        )
    
    def run(self):
        """تشغيل البوت"""
        logger.info("Starting bot...")
        
        # إنشاء Application
        app = Application.builder().token(BotConfig.BOT_TOKEN).build()
        
        # إضافة Handlers
        app.add_handler(CommandHandler("start", self.start_handler))
        app.add_handler(CommandHandler("help", self.help_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.unknown_handler))
        
        # تشغيل البوت
        logger.info("Bot is running...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """نقطة البداية"""
    try:
        bot = OTPBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        # إغلاق اتصال قاعدة البيانات
        if hasattr(bot, 'db'):
            bot.db.close()


if __name__ == '__main__':
    main()
