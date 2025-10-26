"""
AI Content Generation Service using Google Gemini API
"""
import os
import logging
from typing import Dict, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """مولد المحتوى بالذكاء الاصطناعي"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.enabled = bool(self.api_key) and GENAI_AVAILABLE
        
        if self.enabled:
            try:
                genai.configure(api_key=self.api_key)
                # استخدام أحدث موديل متاح (Gemini 2.5 Flash)
                # سريع جداً ومجاني ويدعم العربية بشكل ممتاز
                self.model = genai.GenerativeModel('models/gemini-2.5-flash')
                logger.info("✅ Gemini AI initialized successfully (gemini-2.5-flash)")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                self.enabled = False
    
    def generate_instructions(self, context: Dict) -> str:
        """توليد تعليمات الاستلام"""
        
        school_name = context.get('school_name', 'المدرسة')
        grade = context.get('grade', '')
        section = context.get('section', '')
        
        # نموذج افتراضي (يمكن استبداله بـ API call)
        default_content = f"""
📚 مرحباً بك في نظام تسليم المشاريع الذكي

🎯 **كيف يعمل النظام؟**

1. **التسجيل السريع**: سجل اسمك مرة واحدة فقط
2. **رفع المشروع**: ارفع ملفات مشروعك بسهولة
3. **فحص فوري**: الذكاء الاصطناعي يفحص مشروعك تلقائياً
4. **ملاحظات فورية**: احصل على ملاحظات لتحسين مشروعك
5. **تتبع مباشر**: تابع حالة مشروعك ودرجتك

✅ **الميزات**:
- تسليم آمن ومشفر
- دعم جميع أنواع الملفات
- فحص تلقائي للأخطاء
- نظام تنبيهات ذكي

📱 انضم الآن إلى قروب {school_name} - {grade} {section}
"""
        
        if not self.enabled:
            return default_content.strip()
        
        try:
            prompt = f"""
أنت مساعد ذكي لنظام تعليمي. اكتب تعليمات مختصرة وواضحة للطلاب حول كيفية استخدام نظام تسليم المشاريع.

السياق:
- المدرسة: {school_name}
- الصف: {grade}
- الشعبة: {section}

اكتب التعليمات باللغة العربية، بأسلوب مشجع وواضح، في 5-7 نقاط رئيسية.
"""
            response = self.model.generate_content(prompt)
            generated_text = response.text
            logger.info("✅ AI generated instructions successfully")
            return generated_text.strip()
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            return default_content.strip()
    
    def generate_benefits(self, context: Dict) -> str:
        """توليد فوائد النظام"""
        
        default_content = """
🌟 **لماذا نظام مشروعي الذكي؟**

✅ **سهولة الاستخدام**
تصميم بسيط وسهل يناسب جميع الطلاب

🤖 **ذكاء اصطناعي**
فحص تلقائي وملاحظات فورية لتحسين مشروعك

📊 **متابعة شاملة**
تابع تقدمك ودرجاتك في مكان واحد

🔒 **أمان عالي**
حماية ملفاتك وبياناتك بأحدث التقنيات

⚡ **سرعة فائقة**
رفع وتسليم المشاريع في ثوانٍ معدودة

📱 **من أي مكان**
الوصول من الجوال أو الكمبيوتر بسهولة
"""
        
        if not self.enabled:
            return default_content.strip()
        
        try:
            prompt = """
أنت مساعد ذكي لنظام تعليمي. اكتب قائمة بفوائد استخدام نظام تسليم المشاريع الإلكتروني للطلاب.

اكتب 5-6 فوائد رئيسية باللغة العربية، بأسلوب تسويقي مشجع، مع استخدام الرموز التعبيرية.
"""
            response = self.model.generate_content(prompt)
            generated_text = response.text
            logger.info("✅ AI generated benefits successfully")
            return generated_text.strip()
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            return default_content.strip()
    
    def generate_welcome(self, context: Dict) -> str:
        """توليد رسالة ترحيب"""
        
        student_name = context.get('student_name', 'الطالب')
        school_name = context.get('school_name', 'المدرسة')
        
        default_content = f"""
👋 **مرحباً {student_name}!**

نتمنى لك تجربة مثمرة في {school_name}

🎓 **نصائح للنجاح:**

1. ابدأ مشروعك مبكراً
2. استخدم الذكاء الاصطناعي للمراجعة
3. تابع الملاحظات والتحسينات
4. سلّم قبل الموعد النهائي
5. لا تتردد في السؤال

💪 **نحن هنا لدعمك!**

استمتع بتجربة تعليمية ذكية ومميزة 🚀
"""
        
        if not self.enabled:
            return default_content.strip()
        
        try:
            prompt = f"""
أنت مساعد ذكي لنظام تعليمي. اكتب رسالة ترحيب دافئة للطالب الجديد.

السياق:
- اسم الطالب: {student_name}
- المدرسة: {school_name}

اكتب رسالة ترحيب قصيرة (3-4 جمل) باللغة العربية، مع نصائح بسيطة للنجاح، بأسلوب مشجع وودي.
"""
            response = self.model.generate_content(prompt)
            generated_text = response.text
            logger.info("✅ AI generated welcome message successfully")
            return generated_text.strip()
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            return default_content.strip()


# Global instance
ai_generator = AIContentGenerator()
