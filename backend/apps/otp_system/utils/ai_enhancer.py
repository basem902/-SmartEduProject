"""
AI Enhancement for Project Instructions and Requirements
يستخدم Google Gemini API لتحسين التعليمات والشروط
"""
import os
import json
from django.conf import settings


class AIEnhancer:
    """محسّن النصوص بالذكاء الاصطناعي"""
    
    def __init__(self):
        """تهيئة AI Enhancer"""
        self.api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-pro')
        self.enabled = bool(self.api_key)
    
    def enhance_instructions(self, original_text, project_title='', subject=''):
        """
        تحسين تعليمات المشروع
        
        Args:
            original_text (str): النص الأصلي
            project_title (str): عنوان المشروع
            subject (str): المادة
            
        Returns:
            dict: {
                'enhanced': النص المحسن,
                'suggestions': اقتراحات إضافية,
                'clarity_score': درجة الوضوح
            }
        """
        if not self.enabled:
            return {
                'enhanced': original_text,
                'suggestions': [],
                'clarity_score': 0,
                'error': 'AI غير مفعّل'
            }
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            prompt = f"""
أنت مساعد ذكي متخصص في التعليم. مهمتك تحسين تعليمات المشروع التعليمي لتكون أكثر وضوحاً وتنظيماً.

**معلومات المشروع:**
- العنوان: {project_title}
- المادة: {subject}

**التعليمات الأصلية:**
{original_text}

**المطلوب:**
1. أعد صياغة التعليمات بشكل أكثر وضوحاً وتنظيماً
2. قسّم التعليمات لخطوات مرقمة إذا لزم الأمر
3. أضف تفاصيل مفيدة دون الإطالة
4. استخدم لغة عربية فصيحة وواضحة
5. أضف emojis مناسبة لتسهيل القراءة

**أعطني النتيجة بصيغة JSON:**
{{
    "enhanced": "النص المحسن",
    "suggestions": ["اقتراح 1", "اقتراح 2"],
    "clarity_score": 85
}}
"""
            
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # تنظيف النص (إزالة ```json و```)
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            return result
            
        except Exception as e:
            return {
                'enhanced': original_text,
                'suggestions': [],
                'clarity_score': 0,
                'error': str(e)
            }
    
    def enhance_requirements(self, original_text, project_title=''):
        """
        تحسين شروط التسليم
        
        Args:
            original_text (str): النص الأصلي
            project_title (str): عنوان المشروع
            
        Returns:
            dict: {
                'enhanced': النص المحسن,
                'suggestions': اقتراحات إضافية,
                'completeness_score': درجة الاكتمال
            }
        """
        if not self.enabled:
            return {
                'enhanced': original_text,
                'suggestions': [],
                'completeness_score': 0,
                'error': 'AI غير مفعّل'
            }
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            prompt = f"""
أنت مساعد ذكي متخصص في التعليم. مهمتك تحسين شروط تسليم المشروع التعليمي.

**معلومات المشروع:**
- العنوان: {project_title}

**الشروط الأصلية:**
{original_text}

**المطلوب:**
1. أعد صياغة الشروط بشكل واضح ومحدد
2. رتّب الشروط حسب الأهمية
3. أضف أي شروط مهمة قد تكون مفقودة (مثل: حجم الملف، نوع الملف، التسمية، إلخ)
4. استخدم نقاط واضحة ومرقمة
5. أضف emojis مناسبة

**أعطني النتيجة بصيغة JSON:**
{{
    "enhanced": "النص المحسن",
    "suggestions": ["اقتراح 1", "اقتراح 2"],
    "completeness_score": 90
}}
"""
            
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # تنظيف النص
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            return result
            
        except Exception as e:
            return {
                'enhanced': original_text,
                'suggestions': [],
                'completeness_score': 0,
                'error': str(e)
            }
    
    def generate_default_instructions(self, project_title, subject, grade):
        """
        توليد تعليمات افتراضية للمشروع
        
        Args:
            project_title (str): عنوان المشروع
            subject (str): المادة
            grade (str): الصف
            
        Returns:
            str: تعليمات افتراضية
        """
        if not self.enabled:
            return f"""
📋 تعليمات تسليم مشروع: {project_title}

الخطوات:
1. تحضير المشروع حسب المطلوب
2. حفظ الملف بصيغة مناسبة
3. التأكد من جودة العمل
4. رفع الملف عبر الرابط المخصص
"""
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            prompt = f"""
أنت مساعد ذكي متخصص في التعليم. أنشئ تعليمات واضحة لمشروع تعليمي.

**معلومات المشروع:**
- العنوان: {project_title}
- المادة: {subject}
- الصف: {grade}

**المطلوب:**
أنشئ تعليمات واضحة ومفصلة للطلاب تشمل:
1. مقدمة قصيرة عن المشروع
2. الخطوات المطلوبة بشكل مرقم
3. نصائح مفيدة
4. ما يجب تجنبه

استخدم لغة بسيطة وواضحة مع emojis مناسبة.
"""
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"فشل في توليد تعليمات: {str(e)}"
    
    def generate_default_requirements(self, file_type='pdf', max_size_mb=10):
        """
        توليد شروط افتراضية للتسليم
        
        Args:
            file_type (str): نوع الملف المطلوب
            max_size_mb (int): أقصى حجم بالميجابايت
            
        Returns:
            str: شروط افتراضية
        """
        return f"""
✅ شروط التسليم:

1️⃣ نوع الملف: {file_type.upper()} فقط
2️⃣ الحجم الأقصى: {max_size_mb} ميجابايت
3️⃣ تسمية الملف: اسم الطالب_المشروع
4️⃣ التحقق من عضوية القروب عبر تيليجرام
5️⃣ إدخال رمز التحقق (OTP) بشكل صحيح
6️⃣ التسليم قبل الموعد النهائي

⚠️ ملاحظات مهمة:
- لا تُقبل الملفات التالفة أو المشفرة
- يُرفض التسليم المتأخر
- يجب أن يكون العمل فردياً (ما لم يُذكر خلاف ذلك)
"""


# مثال على الاستخدام:
# enhancer = AIEnhancer()
# result = enhancer.enhance_instructions(
#     "اكتب بحث عن الطاقة المتجددة",
#     project_title="بحث الطاقة",
#     subject="العلوم"
# )
# print(result['enhanced'])
