"""
Professional AI Prompts for Project Content Generation
تصميم prompts احترافية لتوليد محتوى المشاريع
"""

PROFESSIONAL_PROMPTS = {
    'instructions': """أنت معلم سعودي محترف متخصص في المناهج السعودية.

المهمة: توليد 5 تعليمات واضحة لتنفيذ المشروع

السياق:
- اسم المشروع: {project_name}
- المادة: {subject}
- الصف: {grade}
- المرحلة: {level}
- الوصف: {description}

المتطلبات:
1. بالضبط 5 تعليمات (لا أكثر ولا أقل)
2. كل تعليمة في سطر واحد
3. واضحة ومباشرة وقابلة للتنفيذ
4. مناسبة للفئة العمرية ({level} - الصف {grade})
5. خطوات منطقية مرتبة

التنسيق المطلوب (استخدم هذا التنسيق بالضبط):
- [ ] [خطوة واضحة ومحددة]
- [ ] [خطوة واضحة ومحددة]
- [ ] [خطوة واضحة ومحددة]
- [ ] [خطوة واضحة ومحددة]
- [ ] [خطوة واضحة ومحددة]

ملاحظات:
- استخدم لغة بسيطة ومناسبة للطلاب
- كل تعليمة يجب أن تبدأ بـ "- [ ]"
- كل تعليمة في سطر منفصل
- لا تضف أرقام أو ترقيم إضافي
- لا تضف مقدمة أو خاتمة

مثال للتنسيق:
- [ ] ابدأ بقراءة المتطلبات بعناية
- [ ] خطط للمشروع وحدد الخطوات
- [ ] نفذ العمل خطوة بخطوة
- [ ] راجع عملك قبل التسليم
- [ ] تأكد من استيفاء جميع الشروط""",

    'requirements': """أنت معلم سعودي محترف متخصص في المناهج السعودية.

المهمة: توليد 5 شروط واضحة لقبول المشروع

السياق:
- اسم المشروع: {project_name}
- المادة: {subject}
- الصف: {grade}
- المرحلة: {level}
- الوصف: {description}
- الدرجة الكاملة: {max_grade}

المتطلبات:
1. بالضبط 5 شروط (لا أكثر ولا أقل)
2. كل شرط محدد وقابل للقياس
3. شروط أساسية وواقعية
4. واضحة وغير قابلة للتأويل
5. مرتبطة بالمشروع مباشرة

التنسيق المطلوب (استخدم هذا التنسيق بالضبط):
- [ ] [شرط محدد وقابل للقياس]
- [ ] [شرط محدد وقابل للقياس]
- [ ] [شرط محدد وقابل للقياس]
- [ ] [شرط محدد وقابل للقياس]
- [ ] [شرط محدد وقابل للقياس]

ملاحظات:
- ركّز على الجودة والالتزام بالمواصفات
- كل شرط يجب أن يبدأ بـ "- [ ]"
- كل شرط في سطر منفصل
- لا تضف مقدمة أو خاتمة
- استخدم معايير واضحة

مثال للتنسيق:
- [ ] الالتزام بالموعد النهائي المحدد
- [ ] جودة المحتوى والعرض الاحترافي
- [ ] الأصالة وعدم النسخ أو الانتحال
- [ ] التنسيق والإخراج الجيد للعمل
- [ ] اكتمال جميع العناصر المطلوبة""",

    'tips': """أنت معلم سعودي محترف متخصص في المناهج السعودية.

المهمة: توليد 5 نصائح عملية لإنجاح المشروع

السياق:
- اسم المشروع: {project_name}
- المادة: {subject}
- الصف: {grade}
- المرحلة: {level}
- الوصف: {description}

المتطلبات:
1. بالضبط 5 نصائح (لا أكثر ولا أقل)
2. نصائح عملية وقابلة للتطبيق
3. تحفيزية وإيجابية
4. تساعد الطلاب على التميّز
5. بسيطة وسهلة الفهم

التنسيق المطلوب (استخدم هذا التنسيق بالضبط):
💡 [نصيحة مفيدة وعملية]
💡 [نصيحة مفيدة وعملية]
💡 [نصيحة مفيدة وعملية]
💡 [نصيحة مفيدة وعملية]
💡 [نصيحة مفيدة وعملية]

ملاحظات:
- استخدم أسلوب تحفيزي ومشجّع
- كل نصيحة يجب أن تبدأ بـ "💡 "
- كل نصيحة في سطر منفصل
- لا تضف أرقام أو ترقيم
- لا تضف مقدمة أو خاتمة
- كن إيجابياً ومحفّزاً

مثال للتنسيق:
💡 ابدأ مبكراً ولا تؤجل العمل للحظات الأخيرة
💡 استشر معلمك عند الحاجة ولا تتردد في السؤال
💡 تعاون مع زملائك وتبادل الأفكار المفيدة
💡 راجع عملك أكثر من مرة قبل التسليم النهائي
💡 احتفظ بنسخة احتياطية من مشروعك دائماً"""
}


FALLBACK_TEMPLATES = {
    'instructions': [
        '- [ ] ابدأ بقراءة جميع المتطلبات والتعليمات بعناية',
        '- [ ] خطط للمشروع وحدد الخطوات والمهام المطلوبة',
        '- [ ] نفذ العمل خطوة بخطوة بتركيز واهتمام',
        '- [ ] راجع عملك وتأكد من الجودة قبل التسليم',
        '- [ ] تحقق من استيفاء جميع الشروط والمتطلبات'
    ],
    'requirements': [
        '- [ ] الالتزام بالموعد النهائي المحدد للمشروع',
        '- [ ] جودة المحتوى والعرض الاحترافي',
        '- [ ] الأصالة والابتكار وعدم النسخ',
        '- [ ] التنسيق الجيد والإخراج المناسب',
        '- [ ] اكتمال جميع العناصر والمكونات المطلوبة'
    ],
    'tips': [
        '💡 ابدأ مبكراً ولا تؤجل المشروع للحظات الأخيرة',
        '💡 استشر معلمك عند الحاجة ولا تتردد في طرح الأسئلة',
        '💡 تعاون مع زملائك وتبادل الخبرات والأفكار',
        '💡 راجع عملك أكثر من مرة قبل التسليم النهائي',
        '💡 احتفظ بنسخة احتياطية من مشروعك للأمان'
    ]
}


def build_ai_context(project_data, content_type):
    """بناء سياق محسّن للـ AI مع معلومات الصف"""
    from apps.sections.models import SchoolGrade
    
    # استخراج معلومات الصف
    grade_info = {
        'grade_number': 'غير محدد',
        'level': '',
        'level_display': 'غير محدد'
    }
    
    grade_id = project_data.get('grade_id')
    if grade_id:
        try:
            grade = SchoolGrade.objects.get(id=grade_id)
            level_choices = {
                'elementary': 'ابتدائي',
                'middle': 'متوسط',
                'high': 'ثانوي'
            }
            
            grade_info = {
                'grade_number': grade.grade_number,
                'level': grade.level,
                'level_display': level_choices.get(grade.level, grade.level)
            }
        except Exception as e:
            print(f"Error fetching grade info: {e}")
    
    # بناء السياق
    context = {
        'project_name': project_data.get('project_name', project_data.get('title', 'المشروع')),
        'subject': project_data.get('subject', 'المادة'),
        'grade': grade_info['grade_number'],
        'level': grade_info['level_display'],
        'description': project_data.get('description', ''),
        'max_grade': project_data.get('max_grade', 100)
    }
    
    return context


def validate_and_format_ai_response(response_text, content_type, max_items=5):
    """التحقق من صحة وتنسيق الاستجابة"""
    if not response_text or not response_text.strip():
        return '\n'.join(FALLBACK_TEMPLATES.get(content_type, []))
    
    lines = response_text.strip().split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        
        # تخطي الأسطر الفارغة
        if not line:
            continue
        
        # تخطي المقدمات والعناوين
        if line.startswith('#') or line.startswith('**') or ':' in line[:20]:
            continue
        
        # تنسيق التعليمات والشروط
        if content_type in ['instructions', 'requirements']:
            # إزالة أي ترقيم موجود
            line = line.lstrip('0123456789.-) ')
            
            # إضافة checkbox إذا لم يكن موجوداً
            if not line.startswith('- [ ]'):
                line = f"- [ ] {line}"
        
        # تنسيق النصائح
        elif content_type == 'tips':
            # إزالة أي ترقيم أو رموز
            line = line.lstrip('0123456789.-) ')
            
            # إضافة emoji إذا لم يكن موجوداً
            if not line.startswith('💡'):
                line = f"💡 {line}"
        
        formatted_lines.append(line)
        
        # التوقف عند الوصول للحد الأقصى
        if len(formatted_lines) >= max_items:
            break
    
    # إضافة نقاط من الـ fallback إذا كانت أقل من المطلوب
    if len(formatted_lines) < max_items:
        fallback = FALLBACK_TEMPLATES.get(content_type, [])
        while len(formatted_lines) < max_items and len(fallback) > 0:
            # أضف من الـ fallback بالترتيب
            idx = len(formatted_lines)
            if idx < len(fallback):
                formatted_lines.append(fallback[idx])
            else:
                break
    
    return '\n'.join(formatted_lines[:max_items])


def get_fallback_content(content_type):
    """الحصول على محتوى احتياطي"""
    return '\n'.join(FALLBACK_TEMPLATES.get(content_type, []))
