"""
Models for Accounts App
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password


class TeacherPending(models.Model):
    """المعلمون المنتظرون للتفعيل"""
    
    full_name = models.CharField(max_length=100, verbose_name='الاسم الكامل')
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    phone = models.CharField(max_length=10, verbose_name='رقم الجوال')
    school_name = models.CharField(max_length=200, verbose_name='اسم المدرسة')
    activation_code = models.CharField(max_length=6, verbose_name='كود التفعيل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')
    expires_at = models.DateTimeField(verbose_name='تاريخ انتهاء الكود')
    
    class Meta:
        db_table = 'teachers_pending'
        verbose_name = 'معلم منتظر'
        verbose_name_plural = 'معلمون منتظرون'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Teacher(models.Model):
    """المعلمون المفعلون"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='teacher_profile', verbose_name='حساب المستخدم')
    full_name = models.CharField(max_length=100, verbose_name='الاسم الكامل')
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    phone = models.CharField(max_length=10, verbose_name='رقم الجوال')
    school_name = models.CharField(max_length=200, verbose_name='اسم المدرسة')
    password_hash = models.CharField(max_length=255, verbose_name='كلمة المرور المشفرة')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    # Teaching Subjects
    subjects = models.JSONField(
        default=list,
        blank=True,
        verbose_name='المواد الدراسية',
        help_text='قائمة المواد التي يدرسها المعلم'
    )
    
    # Telegram Integration
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True, verbose_name='معرف تيليجرام')
    telegram_username = models.CharField(max_length=100, null=True, blank=True, verbose_name='اسم المستخدم في تيليجرام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='آخر تسجيل دخول')
    
    class Meta:
        db_table = 'teachers'
        verbose_name = 'معلم'
        verbose_name_plural = 'معلمون'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def set_password(self, raw_password: str):
        """تعيين كلمة المرور"""
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password: str) -> bool:
        """التحقق من كلمة المرور"""
        return check_password(raw_password, self.password_hash)


class Settings(models.Model):
    """إعدادات المعلم"""
    
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='settings', verbose_name='المعلم')
    theme = models.CharField(max_length=10, default='light', choices=[('light', 'فاتح'), ('dark', 'داكن')], verbose_name='السمة')
    notifications_enabled = models.BooleanField(default=True, verbose_name='تفعيل الإشعارات')
    language = models.CharField(max_length=2, default='ar', choices=[('ar', 'العربية'), ('en', 'English')], verbose_name='اللغة')
    
    class Meta:
        db_table = 'settings'
        verbose_name = 'إعدادات'
        verbose_name_plural = 'إعدادات'
    
    def __str__(self):
        return f"إعدادات {self.teacher.full_name}"
