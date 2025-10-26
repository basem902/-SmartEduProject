"""
Telegram Bot Configuration
"""
import os
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()


class BotConfig:
    """إعدادات البوت"""
    
    # Telegram Bot Token
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Backend API URL
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
    
    # Secret Key للتوقيع
    SECRET_KEY = os.getenv('OTP_SECRET_KEY', 'your-secret-key')
    
    # Database URL (إذا كنت تريد الاتصال المباشر)
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # Bot Info
    BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', 'YourBot')
    
    @classmethod
    def validate(cls):
        """التحقق من صحة الإعدادات"""
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        if len(cls.BOT_TOKEN) < 40:
            raise ValueError("Invalid BOT_TOKEN format")
        
        return True


# التحقق عند الاستيراد
try:
    BotConfig.validate()
except ValueError as e:
    print(f"⚠️ Configuration Error: {e}")
