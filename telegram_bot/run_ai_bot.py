"""
🚀 مشغل البوت السريع
"""
import sys
import os

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

# إضافة مسار backend للوصول لـ AI Validator
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# تشغيل البوت
from ai_bot import SmartEduAIBot

if __name__ == '__main__':
    print("="*60)
    print("🤖 SmartEdu AI Bot")
    print("📚 بوت فحص المشاريع الطلابية بالذكاء الاصطناعي")
    print("="*60)
    print()
    
    try:
        bot = SmartEduAIBot()
        print("✅ البوت جاهز!")
        print("💡 اذهب إلى Telegram وابحث عن: @SmartEduProjectBot")
        print("📤 أرسل أي ملف للاختبار!")
        print()
        print("⏹️ اضغط Ctrl+C للإيقاف")
        print("="*60)
        print()
        
        bot.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف البوت بنجاح!")
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
