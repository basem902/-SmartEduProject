"""
نظام التحقق من الإدخال والحماية من XSS و SQL Injection
"""
import re
import bleach
from django.core.exceptions import ValidationError


class InputValidator:
    """التحقق من صحة المدخلات وتنظيفها"""
    
    # Regex patterns
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^(05|5)[0-9]{8}$'
    NAME_PATTERN = r'^[\u0621-\u064Aa-zA-Z\s]{2,100}$'
    PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{10,}$'
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """تنظيف النص من HTML و JavaScript"""
        if not text:
            return ""
        
        # إزالة جميع HTML tags
        cleaned = bleach.clean(
            text,
            tags=[],
            attributes={},
            strip=True
        )
        
        # إزالة الأحرف الخطرة
        dangerous_chars = ['<', '>', '"', "'", '&', '`']
        for char in dangerous_chars:
            cleaned = cleaned.replace(char, '')
        
        return cleaned.strip()
    
    @staticmethod
    def validate_email(email: str) -> str:
        """التحقق من صحة البريد الإلكتروني"""
        if not email:
            raise ValidationError("البريد الإلكتروني مطلوب")
        
        email = InputValidator.sanitize_html(email.lower().strip())
        
        if not re.match(InputValidator.EMAIL_PATTERN, email):
            raise ValidationError("صيغة البريد الإلكتروني غير صحيحة")
        
        if len(email) > 255:
            raise ValidationError("البريد الإلكتروني طويل جداً")
        
        return email
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """التحقق من صحة رقم الجوال"""
        if not phone:
            raise ValidationError("رقم الجوال مطلوب")
        
        phone = InputValidator.sanitize_html(phone.strip())
        # إزالة المسافات والشرطات
        phone = phone.replace(' ', '').replace('-', '')
        
        if not re.match(InputValidator.PHONE_PATTERN, phone):
            raise ValidationError("رقم الجوال غير صحيح (يجب أن يبدأ بـ 05 ويتكون من 10 أرقام)")
        
        return phone
    
    @staticmethod
    def validate_name(name: str, field_name: str = "الاسم") -> str:
        """التحقق من صحة الاسم"""
        if not name:
            raise ValidationError(f"{field_name} مطلوب")
        
        name = InputValidator.sanitize_html(name.strip())
        
        if not re.match(InputValidator.NAME_PATTERN, name):
            raise ValidationError(f"{field_name} يجب أن يحتوي على حروف عربية أو إنجليزية فقط")
        
        if len(name) < 2:
            raise ValidationError(f"{field_name} قصير جداً")
        
        if len(name) > 100:
            raise ValidationError(f"{field_name} طويل جداً")
        
        return name
    
    @staticmethod
    def validate_password(password: str) -> str:
        """التحقق من قوة كلمة المرور"""
        if not password:
            raise ValidationError("كلمة المرور مطلوبة")
        
        if len(password) < 10:
            raise ValidationError("كلمة المرور يجب أن تكون 10 أحرف على الأقل")
        
        if not re.match(InputValidator.PASSWORD_PATTERN, password):
            raise ValidationError(
                "كلمة المرور يجب أن تحتوي على: حرف كبير، حرف صغير، رقم، ورمز خاص (@$!%*?&#)"
            )
        
        # التحقق من عدم احتواء كلمات شائعة
        common_passwords = ['password', '12345678', 'qwerty', 'admin', 'user']
        if any(common in password.lower() for common in common_passwords):
            raise ValidationError("كلمة المرور ضعيفة جداً")
        
        return password
    
    @staticmethod
    def validate_text(text: str, min_length: int = 1, max_length: int = 5000, field_name: str = "النص") -> str:
        """التحقق من صحة النص العام"""
        if not text:
            raise ValidationError(f"{field_name} مطلوب")
        
        text = InputValidator.sanitize_html(text.strip())
        
        if len(text) < min_length:
            raise ValidationError(f"{field_name} قصير جداً")
        
        if len(text) > max_length:
            raise ValidationError(f"{field_name} طويل جداً")
        
        return text
    
    @staticmethod
    def validate_number(value: str, min_val: int = None, max_val: int = None, field_name: str = "الرقم") -> int:
        """التحقق من صحة الرقم"""
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} يجب أن يكون رقماً صحيحاً")
        
        if min_val is not None and value < min_val:
            raise ValidationError(f"{field_name} يجب أن يكون {min_val} على الأقل")
        
        if max_val is not None and value > max_val:
            raise ValidationError(f"{field_name} يجب أن يكون {max_val} كحد أقصى")
        
        return value
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """التحقق من أمان اسم الملف"""
        if not filename:
            return False
        
        # منع الأسماء الخطرة
        dangerous_names = ['..', './', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(dangerous in filename for dangerous in dangerous_names):
            return False
        
        # التحقق من الطول
        if len(filename) > 255:
            return False
        
        return True


def sanitize_dict(data: dict) -> dict:
    """تنظيف جميع القيم في القاموس"""
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned[key] = InputValidator.sanitize_html(value)
        elif isinstance(value, dict):
            cleaned[key] = sanitize_dict(value)
        elif isinstance(value, list):
            cleaned[key] = [
                InputValidator.sanitize_html(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            cleaned[key] = value
    return cleaned
