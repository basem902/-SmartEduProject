"""
Serializers for OTP System
"""
from rest_framework import serializers
from .models import ProjectOTP, OTPLog
from apps.projects.models import Project


class OTPInitSerializer(serializers.Serializer):
    """Serializer لطلب رمز OTP"""
    
    project_id = serializers.IntegerField(required=True)
    student_name = serializers.CharField(max_length=100, required=True)
    payload = serializers.CharField(required=True)
    
    def validate_student_name(self, value):
        """التحقق من اسم الطالب"""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('الاسم قصير جداً')
        if len(value) > 100:
            raise serializers.ValidationError('الاسم طويل جداً')
        return value
    
    def validate_project_id(self, value):
        """التحقق من وجود المشروع"""
        try:
            project = Project.objects.get(id=value, is_active=True)
            if not project.section:
                raise serializers.ValidationError('المشروع غير مرتبط بشعبة')
        except Project.DoesNotExist:
            raise serializers.ValidationError('المشروع غير موجود')
        return value


class OTPVerifySerializer(serializers.Serializer):
    """Serializer للتحقق من رمز OTP"""
    
    otp_id = serializers.IntegerField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    
    def validate_code(self, value):
        """التحقق من صحة الكود"""
        value = value.strip()
        if len(value) != 6:
            raise serializers.ValidationError('الرمز يجب أن يكون 6 أرقام')
        if not value.isdigit():
            raise serializers.ValidationError('الرمز يجب أن يحتوي على أرقام فقط')
        return value


class ProjectOTPSerializer(serializers.ModelSerializer):
    """Serializer لعرض بيانات OTP"""
    
    project_title = serializers.CharField(source='project.title', read_only=True)
    section_name = serializers.CharField(source='project.section.section_name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    can_verify = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectOTP
        fields = [
            'id',
            'project',
            'project_title',
            'section_name',
            'student_name',
            'code',
            'status',
            'expires_at',
            'attempts',
            'max_attempts',
            'submit_token',
            'submit_token_expires',
            'telegram_user_id',
            'telegram_username',
            'is_expired',
            'can_verify',
            'created_at',
            'verified_at',
            'used_at'
        ]
        read_only_fields = [
            'code',
            'status',
            'submit_token',
            'telegram_user_id',
            'telegram_username'
        ]
    
    def get_is_expired(self, obj):
        """هل انتهى؟"""
        return obj.is_expired()
    
    def get_can_verify(self, obj):
        """هل يمكن التحقق؟"""
        can, message = obj.can_verify()
        return {'can': can, 'message': message}


class AIEnhanceSerializer(serializers.Serializer):
    """Serializer لتحسين النصوص بالـ AI"""
    
    TYPE_CHOICES = [
        ('instructions', 'تعليمات'),
        ('requirements', 'شروط'),
    ]
    
    text = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=TYPE_CHOICES, required=True)
    project_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_text(self, value):
        """التحقق من النص"""
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('النص قصير جداً')
        if len(value) > 5000:
            raise serializers.ValidationError('النص طويل جداً')
        return value


class OTPLogSerializer(serializers.ModelSerializer):
    """Serializer لعرض سجلات OTP"""
    
    student_name = serializers.CharField(source='otp.student_name', read_only=True)
    
    class Meta:
        model = OTPLog
        fields = [
            'id',
            'otp',
            'student_name',
            'action',
            'details',
            'ip_address',
            'created_at'
        ]
        read_only_fields = fields


class OTPStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات OTP"""
    
    total_requests = serializers.IntegerField()
    verified_count = serializers.IntegerField()
    expired_count = serializers.IntegerField()
    used_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    average_attempts = serializers.FloatField()
    success_rate = serializers.FloatField()
