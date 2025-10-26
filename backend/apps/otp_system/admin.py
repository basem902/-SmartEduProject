"""
Admin configuration for OTP System
"""
from django.contrib import admin
from .models import ProjectOTP, OTPLog


@admin.register(ProjectOTP)
class ProjectOTPAdmin(admin.ModelAdmin):
    """لوحة إدارة رموز OTP"""
    
    list_display = [
        'id',
        'student_name',
        'get_project_title',
        'get_section_name',
        'code',
        'status',
        'telegram_user_id',
        'attempts',
        'created_at',
        'expires_at'
    ]
    
    list_filter = [
        'status',
        'created_at',
        'expires_at'
    ]
    
    search_fields = [
        'student_name',
        'code',
        'telegram_username',
        'project__title'
    ]
    
    readonly_fields = [
        'code',
        'submit_token',
        'telegram_user_id',
        'telegram_chat_id',
        'telegram_username',
        'ip_address',
        'signed_payload',
        'created_at',
        'updated_at',
        'verified_at',
        'used_at'
    ]
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': (
                'project',
                'student_name',
                'status'
            )
        }),
        ('بيانات تيليجرام', {
            'fields': (
                'telegram_user_id',
                'telegram_chat_id',
                'telegram_username'
            )
        }),
        ('الرمز والأمان', {
            'fields': (
                'code',
                'expires_at',
                'attempts',
                'max_attempts',
                'submit_token',
                'submit_token_expires',
                'signed_payload'
            )
        }),
        ('معلومات إضافية', {
            'fields': (
                'ip_address',
                'created_at',
                'updated_at',
                'verified_at',
                'used_at'
            )
        })
    )
    
    ordering = ['-created_at']
    
    def get_project_title(self, obj):
        """عنوان المشروع"""
        return obj.project.title
    get_project_title.short_description = 'المشروع'
    
    def get_section_name(self, obj):
        """اسم الشعبة"""
        if obj.project.section:
            return obj.project.section.section_name
        return '-'
    get_section_name.short_description = 'الشعبة'
    
    def has_add_permission(self, request):
        """منع الإضافة من Admin"""
        return False


@admin.register(OTPLog)
class OTPLogAdmin(admin.ModelAdmin):
    """لوحة إدارة سجلات OTP"""
    
    list_display = [
        'id',
        'get_student_name',
        'action',
        'ip_address',
        'created_at'
    ]
    
    list_filter = [
        'action',
        'created_at'
    ]
    
    search_fields = [
        'otp__student_name',
        'otp__code',
        'details'
    ]
    
    readonly_fields = [
        'otp',
        'action',
        'details',
        'ip_address',
        'user_agent',
        'created_at'
    ]
    
    ordering = ['-created_at']
    
    def get_student_name(self, obj):
        """اسم الطالب"""
        return obj.otp.student_name
    get_student_name.short_description = 'الطالب'
    
    def has_add_permission(self, request):
        """منع الإضافة من Admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """منع التعديل"""
        return False
