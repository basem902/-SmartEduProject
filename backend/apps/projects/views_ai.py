"""
AI Content Generation for Projects using Google Gemini
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import Teacher
from django.conf import settings
import google.generativeai as genai
import logging
from .prompts import (
    PROFESSIONAL_PROMPTS,
    build_ai_context,
    validate_and_format_ai_response,
    get_fallback_content
)

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')  # Latest stable & fast model


def get_teacher_from_request(request):
    try:
        if hasattr(request.user, 'teacher_profile'):
            return request.user.teacher_profile
        return Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_project_content(request):
    try:
        teacher = get_teacher_from_request(request)
        if not teacher:
            return Response({'error': 'المعلم غير موجود'}, status=status.HTTP_404_NOT_FOUND)
        
        content_type = request.data.get('content_type')
        context = request.data.get('context', {})
        max_items = context.get('max_items', 5)  # Default: 5 items
        
        if not content_type or content_type not in ['description', 'instructions', 'requirements', 'tips']:
            return Response({'error': 'content_type غير صحيح'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Build context from request
        project_data = {
            'title': context.get('project_name', ''),
            'project_name': context.get('project_name', ''),
            'subject': context.get('subject', ''),
            'description': context.get('description', ''),
            'grade_id': context.get('grade_id'),
            'max_grade': context.get('max_grade', 100)
        }
        
        # Log received data for debugging
        logger.info(f"📥 AI Request - content_type: {content_type}")
        logger.info(f"📥 Context received: {context}")
        
        # Title is optional for now (can use subject as fallback)
        if not project_data['title']:
            project_data['title'] = project_data.get('subject', 'المشروع')
            logger.warning(f"⚠️ No title provided, using fallback: {project_data['title']}")
        
        logger.info(f"🤖 Generating {content_type} for: {project_data['title'][:50]} (max_items={max_items})")
        
        # Generate content
        if content_type == 'description':
            content = generate_description_new(project_data)
        else:
            content = generate_structured_content(content_type, project_data, max_items)
        
        return Response({
            'success': True,
            'content': content,
            'generated_text': content,  # For compatibility
            'items_count': len(content.split('\n')) if content_type != 'description' else 0
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"AI Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_with_gemini(prompt):
    """استدعاء Gemini API"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        return None


def generate_structured_content(content_type, project_data, max_items=5):
    """توليد محتوى منظم (تعليمات، شروط، نصائح) - نسخة محسّنة"""
    try:
        # Build AI context
        ai_context = build_ai_context(project_data, content_type)
        
        # Get professional prompt template
        prompt_template = PROFESSIONAL_PROMPTS.get(content_type)
        if not prompt_template:
            logger.warning(f"No prompt template for {content_type}")
            return get_fallback_content(content_type)
        
        # Format prompt with context
        prompt = prompt_template.format(**ai_context)
        
        logger.info(f"Sending prompt to Gemini for {content_type}")
        
        # Call Gemini API
        response_text = generate_with_gemini(prompt)
        
        if not response_text:
            logger.warning(f"Gemini returned empty response for {content_type}")
            return get_fallback_content(content_type)
        
        # Validate and format response
        formatted_content = validate_and_format_ai_response(
            response_text,
            content_type,
            max_items
        )
        
        logger.info(f"Successfully generated {content_type} with {len(formatted_content.split(chr(10)))} items")
        
        return formatted_content
        
    except Exception as e:
        logger.error(f"Error in generate_structured_content: {str(e)}")
        return get_fallback_content(content_type)


def generate_description_new(project_data):
    """توليد وصف المشروع - نسخة محسّنة"""
    try:
        title = project_data.get('title', '')
        subject = project_data.get('subject', '')
        description = project_data.get('description', '')
        
        # بناء prompt بسيط للوصف
        prompt = f"""أنت معلم سعودي محترف.

اكتب وصفاً تعليمياً احترافياً (3-4 جمل) لمشروع:

العنوان: {title}
المادة: {subject}
{f'السياق: {description}' if description else ''}

الوصف يجب أن:
- يوضح الهدف التعليمي
- يكون محفزاً ومشجعاً
- بلغة عربية فصحى واضحة
- 3-4 جمل فقط

اكتب الوصف مباشرة:"""
        
        result = generate_with_gemini(prompt)
        
        if not result:
            return f"هذا المشروع يهدف إلى تطوير مهارات الطلاب في {subject} من خلال {title}. سيعمل الطلاب على تطبيق المفاهيم النظرية بشكل عملي."
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        return f"مشروع تعليمي في مادة {subject}."


def generate_description(title, subject, context=None):
    """توليد وصف المشروع"""
    context = context or {}
    description = context.get('description', '')
    
    # كشف المشاريع الحكومية من العنوان أو الوصف
    search_text = f"{title.lower()} {description.lower()}"
    is_gov_project = any(keyword in search_text for keyword in 
        ['فيديو', 'مقطع', 'سابك', 'نيوم', 'القدية', 'مشروع حكومي', 'مشاريع حكومية', 
         'البحر الأحمر', 'روشن', 'أمالا', 'لاين', 'الدرعية', 'spark', 'وادي التقنية'])
    
    if is_gov_project:
        prompt = f"""أنت معلم محترف في المملكة العربية السعودية.
اكتب وصفاً احترافياً لمشروع: "{title}"
المادة: {subject}

الوصف يجب أن يوضح:
- أن المشروع فردي (كل طالب له فيديو خاص)
- مدة الفيديو 30 ثانية
- آخر 5 ثوانٍ تحتوي على: الاسم الرباعي، الصف، الشعبة
- يركز على المشاريع الحكومية السعودية
- بأسلوب محفز ومشجع

اكتب الوصف مباشرة (3-4 جمل):"""
    else:
        prompt = f"""أنت معلم محترف في المملكة العربية السعودية.
اكتب وصفاً تعليمياً احترافياً لمشروع: "{title}"
المادة: {subject}

الوصف يجب أن يكون:
- 3-4 جمل واضحة ومفصلة
- يوضح الهدف التعليمي والمهارات المكتسبة
- يشجع على التفكير الإبداعي والابتكار
- بلغة عربية فصحى سهلة ومشوقة

اكتب الوصف مباشرة:"""

    result = generate_with_gemini(prompt)
    return result or f"هذا المشروع يهدف إلى تطوير مهارات الطلاب في {subject} من خلال {title}. سيعمل الطلاب على تطبيق المفاهيم النظرية بشكل عملي وتطوير مهارات البحث والتحليل والعرض الاحترافي."


def generate_instructions(title, subject, context=None):
    """توليد تعليمات المشروع"""
    context = context or {}
    description = context.get('description', '')
    
    # كشف المشاريع الحكومية من العنوان أو الوصف
    search_text = f"{title.lower()} {description.lower()}"
    is_gov_project = any(keyword in search_text for keyword in 
        ['فيديو', 'مقطع', 'سابك', 'نيوم', 'القدية', 'مشروع حكومي', 'مشاريع حكومية',
         'البحر الأحمر', 'روشن', 'أمالا', 'لاين', 'الدرعية', 'spark', 'وادي التقنية'])
    
    # بناء معلومات المشروع
    project_info = f'المشروع: "{title}"\nالمادة: {subject}'
    if description:
        project_info += f'\n\nوصف المشروع:\n{description}'
    
    if is_gov_project:
        prompt = f"""أنت معلم محترف للمهارات الرقمية. بناءً على المعلومات التالية، اكتب تعليمات تنفيذ تفصيلية:

{project_info}

التعليمات يجب أن تشمل:

**1. خطوات التنفيذ (6-8 خطوات مرقمة):**
- استخدام برامج المونتاج (Shotcut أو غيره)
- اختيار المشروع الحكومي
- جمع الصور والفيديوهات
- المونتاج والتأثيرات
- إضافة شاشة النهاية بالبيانات
- المراجعة والتصدير

**2. قائمة المشاريع المقترحة (10 مشاريع):**
سابك، نيوم، القدية، البحر الأحمر، روشن، أمالا، ذا لاين، بوابة الدرعية، SPARK، وادي التقنية

اكتب التعليمات بشكل احترافي ومتوافق مع الوصف أعلاه:"""
    else:
        prompt = f"""أنت معلم محترف. بناءً على المعلومات التالية، اكتب تعليمات واضحة ومفصلة:

{project_info}

التعليمات يجب أن تكون:
- 6-8 خطوات محددة ومفصلة
- متوافقة تماماً مع وصف المشروع
- واضحة وعملية وقابلة للتطبيق
- مرتبة منطقياً من البداية للنهاية
- تتضمن أدوات أو برامج محددة إن أمكن
- مرقمة (1. 2. 3. ...)

اكتب التعليمات مباشرة:"""

    result = generate_with_gemini(prompt)
    return result or """1. اقرأ متطلبات المشروع بعناية وحدد الأهداف
2. قسّم العمل إلى مراحل واضحة مع جدول زمني
3. ابحث عن مصادر موثوقة وجمع المعلومات
4. خطط للتنفيذ واختر الأدوات المناسبة
5. نفّذ المشروع خطوة بخطوة حسب الخطة
6. راجع العمل واطلب ملاحظات من زملائك
7. أجرِ التعديلات النهائية قبل التسليم"""


def generate_requirements(title, subject, context=None):
    """توليد متطلبات المشروع"""
    context = context or {}
    description = context.get('description', '')
    
    # كشف المشاريع الحكومية من العنوان أو الوصف
    search_text = f"{title.lower()} {description.lower()}"
    is_gov_project = any(keyword in search_text for keyword in 
        ['فيديو', 'مقطع', 'سابك', 'نيوم', 'القدية', 'مشروع حكومي', 'مشاريع حكومية',
         'البحر الأحمر', 'روشن', 'أمالا', 'لاين', 'الدرعية', 'spark', 'وادي التقنية'])
    
    # بناء معلومات المشروع
    project_info = f'المشروع: "{title}"\nالمادة: {subject}'
    if description:
        project_info += f'\n\nوصف المشروع:\n{description}'
    
    if is_gov_project:
        prompt = f"""أنت معلم محترف. بناءً على المعلومات التالية، اكتب الشروط والمتطلبات:

{project_info}

الشروط يجب أن تشمل وتتوافق مع الوصف:

**المتطلبات العامة:**
- عمل فردي (كل طالب فيديو خاص)
- ممنوع تكرار نفس المشروع الحكومي بين الطلاب
- المدة: 30 ثانية بالضبط

**المتطلبات التقنية:**
- جودة الفيديو (HD 1080p أو أعلى)
- الصيغة المطلوبة (MP4)
- الحجم الأقصى للملف

**محتوى الفيديو:**
- بداية: تعريف بسيط بالمشروع الحكومي
- المحتوى: صور وفيديوهات مناسبة للموضوع
- النهاية (5 ثوانٍ): الاسم الرباعي + الصف + الشعبة

**الجودة:**
- الصور والمقاطع تناسب الموضوع
- مونتاج احترافي
- موسيقى مناسبة (إن وُجدت)

اكتب الشروط بشكل واضح ومفصل (7-10 نقاط):"""
    else:
        prompt = f"""أنت معلم محترف. بناءً على المعلومات التالية، اكتب متطلبات واضحة ومحددة:

{project_info}

المتطلبات يجب أن تتوافق مع الوصف وتشمل:
- طريقة العمل (فردي أو جماعي) وعدد الأعضاء
- نوع الملفات المطلوبة والصيغ المقبولة
- معايير الجودة والتقييم
- المتطلبات التقنية (برامج، أدوات، إلخ)
- الحد الأقصى للحجم أو المدة
- توثيق المصادر
- 7-10 نقاط

استخدم النقاط (-) وكن محدداً ودقيقاً:"""

    result = generate_with_gemini(prompt)
    return result or """- العمل ضمن فريق (3-5 أعضاء) أو فردي حسب المشروع
- تقديم ملف PDF أو DOCX للتقرير النهائي
- استخدام مصادر موثوقة وتوثيقها بشكل صحيح
- الالتزام بموعد التسليم المحدد
- جودة العرض والتنسيق الاحترافي
- حجم الملف لا يتجاوز 50 MB
- تضمين قائمة بالمراجع والمصادر المستخدمة"""


def generate_tips(title, subject, context=None):
    """توليد نصائح للمشروع"""
    context = context or {}
    description = context.get('description', '')
    instructions = context.get('instructions', '')
    requirements = context.get('requirements', '')
    
    # كشف المشاريع الحكومية من العنوان أو الوصف
    search_text = f"{title.lower()} {description.lower()}"
    is_gov_project = any(keyword in search_text for keyword in 
        ['فيديو', 'مقطع', 'سابك', 'نيوم', 'القدية', 'مشروع حكومي', 'مشاريع حكومية',
         'البحر الأحمر', 'روشن', 'أمالا', 'لاين', 'الدرعية', 'spark', 'وادي التقنية'])
    
    # بناء الـ prompt الذكي بناءً على التعليمات والشروط
    base_info = f"""المشروع: "{title}"
المادة: {subject}"""
    
    if instructions:
        base_info += f"\n\n**التعليمات المقدمة:**\n{instructions}"
    
    if requirements:
        base_info += f"\n\n**الشروط المحددة:**\n{requirements}"
    
    if is_gov_project:
        prompt = f"""أنت معلم محترف ومحفز. استناداً إلى المعلومات التالية، اكتب نصائح عملية وقيمة للطلاب:

{base_info}

النصائح يجب أن:
- تكون متوافقة مع التعليمات والشروط المذكورة أعلاه
- تساعد الطلاب على تحقيق المتطلبات بنجاح
- تركز على: التخطيط، التنفيذ، الجودة، إدارة الوقت
- تكون عملية وقابلة للتطبيق مباشرة
- محفزة وإيجابية
- 7-10 نصائح
- بنقاط (-)

اكتب النصائح مباشرة:"""
    else:
        prompt = f"""أنت معلم محترف ومحفز. استناداً إلى المعلومات التالية، اكتب نصائح عملية وقيمة للطلاب:

{base_info}

النصائح يجب أن:
- تكون متوافقة مع التعليمات والشروط المذكورة أعلاه
- تساعد الطلاب على تحقيق المتطلبات بنجاح
- عملية وقابلة للتطبيق فوراً
- تحفيزية وإيجابية ومشجعة
- تغطي جوانب مختلفة (التخطيط، التنفيذ، الجودة، التعاون)
- مكتوبة بأسلوب ودي وداعم
- 7-10 نصائح
- بنقاط (-)

اكتب النصائح مباشرة:"""

    result = generate_with_gemini(prompt)
    return result or """- ابدأ مبكراً ولا تؤجل العمل للحظة الأخيرة
- خطط جيداً وضع جدولاً زمنياً واقعياً
- اقسم المشروع لمهام صغيرة سهلة الإنجاز
- استخدم مصادر متنوعة وموثوقة
- تعاون مع زملائك واستفد من خبراتهم
- لا تتردد في سؤال معلمك عند الحاجة
- راجع عملك عدة مرات قبل التسليم النهائي
- كن مبدعاً ومميزاً في عرضك"""
