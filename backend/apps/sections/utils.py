"""
Utility Functions for Sections App
"""
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import re


class LinkGenerator:
    """مولد الروابط الذكية"""
    
    @staticmethod
    def generate_join_token():
        """توليد رمز آمن للانضمام"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_join_link(section_id, token, request=None):
        """توليد رابط الانضمام الكامل"""
        # استخدام FRONTEND_URL من settings دائماً
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
        
        return f"{base_url}/pages/join.html?token={token}"
    
    @staticmethod
    def verify_token_signature(token, section_id):
        """التحقق من صحة التوقيع"""
        # هذه دالة بسيطة للتحقق - يمكن تحسينها لاحقاً
        return len(token) == 43  # طول token_urlsafe(32)


class LinkValidator:
    """فحص صحة الروابط"""
    
    # Regex patterns
    WHATSAPP_PATTERN = r'(https?://)?(chat\.whatsapp\.com|wa\.me)/.+'
    TELEGRAM_PATTERN = r'(https?://)?t\.me/.+'
    
    @staticmethod
    def validate_whatsapp_link(link):
        """التحقق من صحة رابط واتساب"""
        if not link:
            return False, "الرابط مطلوب"
        
        if not re.match(LinkValidator.WHATSAPP_PATTERN, link):
            return False, "رابط واتساب غير صحيح"
        
        # التأكد من وجود https
        if not link.startswith('https://'):
            return False, "الرابط يجب أن يبدأ بـ https://"
        
        return True, "رابط صحيح"
    
    @staticmethod
    def validate_telegram_link(link):
        """التحقق من صحة رابط تيليجرام"""
        if not link:
            return False, "الرابط مطلوب"
        
        if not re.match(LinkValidator.TELEGRAM_PATTERN, link):
            return False, "رابط تيليجرام غير صحيح"
        
        # التأكد من وجود https
        if not link.startswith('https://'):
            return False, "الرابط يجب أن يبدأ بـ https://"
        
        return True, "رابط صحيح"
    
    @staticmethod
    def validate_platform_links(platform, whatsapp_link, telegram_link):
        """التحقق من الروابط حسب المنصة"""
        errors = {}
        
        if platform == 'whatsapp' or platform == 'both':
            is_valid, message = LinkValidator.validate_whatsapp_link(whatsapp_link)
            if not is_valid:
                errors['whatsapp_link'] = message
        
        if platform == 'telegram' or platform == 'both':
            is_valid, message = LinkValidator.validate_telegram_link(telegram_link)
            if not is_valid:
                errors['telegram_link'] = message
        
        return len(errors) == 0, errors


class IPHelper:
    """مساعد للتعامل مع عناوين IP"""
    
    @staticmethod
    def get_client_ip(request):
        """الحصول على IP الحقيقي للمستخدم"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def is_valid_ip(ip_address):
        """التحقق من صحة عنوان IP"""
        try:
            import ipaddress
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False


class StatsCalculator:
    """حساب الإحصائيات"""
    
    @staticmethod
    def calculate_section_stats(section):
        """حساب إحصائيات الشعبة"""
        registrations = section.registered_students.all()
        total = registrations.count()
        joined = registrations.filter(joined_telegram=True).count()
        
        join_rate = (joined / total * 100) if total > 0 else 0
        
        return {
            'total_registrations': total,
            'joined_count': joined,
            'pending_count': total - joined,
            'join_rate': round(join_rate, 2)
        }
    
    @staticmethod
    def calculate_grade_stats(grade):
        """حساب إحصائيات الصف"""
        sections = grade.sections.filter(is_active=True)
        total_sections = sections.count()
        total_students = sum(s.total_students for s in sections)
        
        # إحصائيات الروابط
        links = [s.link for s in sections if hasattr(s, 'link')]
        total_views = sum(link.view_count for link in links)
        total_joins = sum(link.join_count for link in links)
        
        return {
            'total_sections': total_sections,
            'total_students': total_students,
            'total_views': total_views,
            'total_joins': total_joins,
            'avg_students_per_section': round(total_students / total_sections, 2) if total_sections > 0 else 0
        }
    
    @staticmethod
    def calculate_teacher_stats(teacher):
        """حساب إحصائيات المعلم"""
        grades = teacher.grades.filter(is_active=True)
        sections = []
        for grade in grades:
            sections.extend(grade.sections.filter(is_active=True))
        
        total_grades = grades.count()
        total_sections = len(sections)
        total_students = sum(s.total_students for s in sections)
        
        return {
            'total_grades': total_grades,
            'total_sections': total_sections,
            'total_students': total_students
        }


class NameCleaner:
    """تنظيف وتوحيد الأسماء"""
    
    @staticmethod
    def clean_student_name(name):
        """تنظيف اسم الطالب"""
        # إزالة المسافات الزائدة
        name = ' '.join(name.split())
        
        # إزالة الأحرف الخاصة
        name = re.sub(r'[^\u0621-\u064Aa-zA-Z\s]', '', name)
        
        # تحويل أول حرف من كل كلمة لحرف كبير
        name = name.title()
        
        return name.strip()
    
    @staticmethod
    def normalize_school_name(school_name):
        """توحيد اسم المدرسة"""
        # تنظيف عام
        school_name = ' '.join(school_name.split())
        
        # استبدال الكلمات الشائعة
        replacements = {
            'مدرسه': 'مدرسة',
            'الاولى': 'الأولى',
            'الثانيه': 'الثانية',
        }
        
        for old, new in replacements.items():
            school_name = school_name.replace(old, new)
        
        return school_name.strip()


class SectionHelper:
    """مساعد لعمليات الشُعب"""
    
    @staticmethod
    def generate_section_name(section_number):
        """توليد اسم الشعبة"""
        return f"شعبة {section_number}"
    
    @staticmethod
    def bulk_create_sections(grade, count):
        """إنشاء عدة شُعب دفعة واحدة"""
        from .models import Section
        
        sections = []
        for i in range(1, count + 1):
            section = Section(
                grade=grade,
                section_number=i,
                section_name=SectionHelper.generate_section_name(i)
            )
            sections.append(section)
        
        return Section.objects.bulk_create(sections)
    
    @staticmethod
    def create_sections_from_list(grade, sections_list):
        """إنشاء شُعب من قائمة محددة (الشُعب المختارة فقط)"""
        from .models import Section
        
        sections = []
        for i, section_name in enumerate(sections_list, start=1):
            section = Section(
                grade=grade,
                section_number=i,
                section_name=section_name  # الاسم الفعلي المختار (أ، ب، ج...)
            )
            sections.append(section)
        
        return Section.objects.bulk_create(sections)
    
    @staticmethod
    def check_duplicate_registration(section, full_name):
        """التحقق من التسجيل المكرر"""
        from .models import StudentRegistration
        
        # تنظيف الاسم
        clean_name = NameCleaner.clean_student_name(full_name)
        
        # البحث عن تسجيل مشابه
        return StudentRegistration.objects.filter(
            section=section,
            full_name__iexact=clean_name
        ).exists()


class ArabicNameNormalizer:
    """تطبيع الأسماء العربية للمقارنة"""
    
    @staticmethod
    def normalize(name):
        """
        تطبيع الاسم العربي
        - إزالة التشكيل
        - توحيد الهمزات
        - إزالة المسافات الزائدة
        """
        import re
        
        if not name:
            return ''
        
        # إزالة التشكيل
        name = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', name)
        
        # توحيد الهمزات
        name = name.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        name = name.replace('ؤ', 'و').replace('ئ', 'ي').replace('ة', 'ه')
        
        # إزالة المسافات الزائدة
        name = ' '.join(name.split())
        
        # تحويل لصغير
        name = name.strip().lower()
        
        return name
    
    @staticmethod
    def calculate_similarity(name1, name2):
        """حساب نسبة التشابه بين اسمين"""
        from difflib import SequenceMatcher
        
        # تطبيع الأسماء
        norm1 = ArabicNameNormalizer.normalize(name1)
        norm2 = ArabicNameNormalizer.normalize(name2)
        
        # حساب التشابه
        return SequenceMatcher(None, norm1, norm2).ratio() * 100


class StudentDuplicateChecker:
    """التحقق من تكرار تسجيل الطلاب"""
    
    @staticmethod
    def check_duplicate(teacher_id, grade_id, section_id, full_name):
        """
        التحقق من وجود طالب مشابه
        
        Returns:
        {
            'is_duplicate': bool,
            'similar_name': str or None,
            'similarity': float,
            'message': str
        }
        """
        from .models import StudentRegistration
        
        # تطبيع الاسم
        normalized = ArabicNameNormalizer.normalize(full_name)
        
        # الحصول على الاسم الأول
        first_name = normalized.split()[0] if normalized.split() else ''
        
        if not first_name:
            return {
                'is_duplicate': False,
                'similar_name': None,
                'similarity': 0,
                'message': ''
            }
        
        # البحث عن أسماء مشابهة
        similar_students = StudentRegistration.objects.filter(
            teacher_id=teacher_id,
            grade_id=grade_id,
            section_id=section_id,
            normalized_name__icontains=first_name
        )
        
        # فحص التشابه
        for student in similar_students:
            similarity = ArabicNameNormalizer.calculate_similarity(
                normalized,
                student.normalized_name
            )
            
            # إذا كان التشابه أكثر من 70%
            if similarity > 70:
                return {
                    'is_duplicate': True,
                    'similar_name': student.full_name,
                    'similarity': similarity,
                    'message': 'يوجد طالب مسجل باسم مشابه. الرجاء إدخال الاسم الرباعي الكامل'
                }
        
        return {
            'is_duplicate': False,
            'similar_name': None,
            'similarity': 0,
            'message': ''
        }


class IPAddressHelper:
    """مساعد للحصول على IP Address"""
    
    @staticmethod
    def get_client_ip(request):
        """الحصول على IP الحقيقي للمستخدم"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
