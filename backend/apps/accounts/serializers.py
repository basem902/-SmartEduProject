"""
Serializers for Accounts App
"""
from rest_framework import serializers
from .models import Teacher, TeacherPending, Settings
from utils.validation import InputValidator


class RegisterSerializer(serializers.Serializer):
    """Serializer للتسجيل"""
    
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=10)
    school_name = serializers.CharField(max_length=200)
    
    def validate_full_name(self, value):
        """التحقق من الاسم الكامل"""
        return InputValidator.validate_name(value, "الاسم الكامل")
    
    def validate_email(self, value):
        """التحقق من البريد الإلكتروني"""
        value = InputValidator.validate_email(value)
        
        # التحقق من عدم وجود البريد في المعلمين المفعلين
        if Teacher.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد مسجل مسبقاً")
        
        return value
    
    def validate_phone(self, value):
        """التحقق من رقم الجوال"""
        return InputValidator.validate_phone(value)
    
    def validate_school_name(self, value):
        """التحقق من اسم المدرسة"""
        return InputValidator.validate_text(value, min_length=3, max_length=200, field_name="اسم المدرسة")


class ActivateSerializer(serializers.Serializer):
    """Serializer للتفعيل"""
    
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    
    def validate_email(self, value):
        return InputValidator.validate_email(value)
    
    def validate_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("كود التفعيل يجب أن يتكون من 6 أرقام")
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer لتسجيل الدخول"""
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate_email(self, value):
        return InputValidator.validate_email(value)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer لتغيير كلمة المرور"""
    
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=10)
    
    def validate_new_password(self, value):
        return InputValidator.validate_password(value)


class TeacherSerializer(serializers.ModelSerializer):
    """Serializer للمعلم"""
    
    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'email', 'phone', 'school_name', 'is_active', 'created_at', 'last_login']
        read_only_fields = ['id', 'created_at', 'last_login']


class SettingsSerializer(serializers.ModelSerializer):
    """Serializer للإعدادات"""
    
    class Meta:
        model = Settings
        fields = ['theme', 'notifications_enabled', 'language']
