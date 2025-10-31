"""
Utility functions for Projects App
"""
import re
import unicodedata


def normalize_arabic_name(name):
    """
    تطبيع الأسماء العربية للتعامل مع الأخطاء الإملائية والاختلافات
    
    Args:
        name (str): الاسم الأصلي
        
    Returns:
        str: الاسم المطبّع
        
    Examples:
        >>> normalize_arabic_name("محمد أحمد علي")
        'محمد احمد علي'
        >>> normalize_arabic_name("  فاطمة   الزهراء  ")
        'فاطمه الزهراء'
    """
    if not name:
        return ""
    
    # 1. إزالة المسافات الزائدة
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)
    
    # 2. توحيد الألف
    name = name.replace('أ', 'ا')
    name = name.replace('إ', 'ا')
    name = name.replace('آ', 'ا')
    name = name.replace('ٱ', 'ا')
    
    # 3. توحيد التاء المربوطة والهاء
    name = name.replace('ة', 'ه')
    
    # 4. توحيد الياء
    name = name.replace('ى', 'ي')
    name = name.replace('ئ', 'ي')
    
    # 5. إزالة الحركات (التشكيل)
    arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
    name = arabic_diacritics.sub('', name)
    
    # 6. إزالة علامات الترقيم والرموز الخاصة
    name = re.sub(r'[^\w\s]', '', name, flags=re.UNICODE)
    
    # 7. تحويل إلى lowercase (للحروف الإنجليزية إن وجدت)
    name = name.lower()
    
    return name


def calculate_name_similarity(name1, name2):
    """
    حساب نسبة التشابه بين اسمين (Levenshtein Distance)
    
    Args:
        name1 (str): الاسم الأول
        name2 (str): الاسم الثاني
        
    Returns:
        float: نسبة التشابه (0-1)
    """
    # تطبيع الأسماء أولاً
    name1 = normalize_arabic_name(name1)
    name2 = normalize_arabic_name(name2)
    
    # Levenshtein Distance
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    distance = levenshtein_distance(name1, name2)
    max_len = max(len(name1), len(name2))
    
    if max_len == 0:
        return 1.0
    
    similarity = 1 - (distance / max_len)
    return similarity


def validate_full_name(name):
    """
    التحقق من صحة الاسم الرباعي
    
    Args:
        name (str): الاسم الكامل
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "الاسم مطلوب"
    
    # إزالة المسافات الزائدة
    name = name.strip()
    
    # التحقق من الطول
    if len(name) < 6:
        return False, "الاسم قصير جداً"
    
    if len(name) > 100:
        return False, "الاسم طويل جداً"
    
    # التحقق من أن الاسم يحتوي على أحرف عربية
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    if not arabic_pattern.search(name):
        return False, "يجب أن يحتوي الاسم على أحرف عربية"
    
    # التحقق من عدد الكلمات (يجب أن يكون 3 أو 4)
    words = name.split()
    if len(words) < 3:
        return False, "يرجى إدخال الاسم الثلاثي أو الرباعي على الأقل"
    
    if len(words) > 5:
        return False, "الاسم طويل جداً، يرجى إدخال الاسم الرباعي فقط"
    
    # التحقق من أن كل كلمة تحتوي على حرفين على الأقل
    for word in words:
        if len(word) < 2:
            return False, f"الاسم '{word}' قصير جداً"
    
    return True, ""


def find_similar_students(input_name, students_queryset, threshold=0.85):
    """
    البحث عن طلاب مشابهين بناءً على الاسم
    
    Args:
        input_name (str): الاسم المدخل
        students_queryset: QuerySet للطلاب
        threshold (float): نسبة التشابه المطلوبة (0-1)
        
    Returns:
        list: قائمة الطلاب المشابهين مع نسبة التشابه
    """
    normalized_input = normalize_arabic_name(input_name)
    results = []
    
    for student in students_queryset:
        similarity = calculate_name_similarity(input_name, student.full_name)
        
        if similarity >= threshold:
            results.append({
                'student': student,
                'similarity': similarity,
                'original_name': student.full_name,
                'normalized_name': student.normalized_name
            })
    
    # ترتيب حسب نسبة التشابه
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return results
