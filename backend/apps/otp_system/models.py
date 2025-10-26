"""
Models for OTP System
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets


class ProjectOTP(models.Model):
    """
    رموز OTP لتسليم المشاريع
    
    السيناريو:
    1. الطالب يطلب رمز OTP
    2. النظام يتحقق من أن المشروع مرتبط بشعبة
    3. يرسل الطالب لبوت تيليجرام
    4. البوت يتحقق من عضوية الطالب في قروب الشعبة
    5. البوت يرسل الرمز للطالب
    6. الطالب يدخل الرمز في الموقع
    7. النظام يصدر submit_token
    8. الطالب يستخدم الـ token لرفع المشروع
    """
    
    STATUS_CHOICES = [
        ('pending', 'بانتظار التحقق'),
        ('verified', 'تم التحقق'),
        ('used', 'مستخدم'),
        ('expired', 'منتهي')
    ]
    
    # الربط
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='otp_records',
        verbose_name='المشروع'
    )
    
    student_name = models.CharField(
        max_length=100,
        verbose_name='اسم الطالب'
    )
    
    # بيانات تيليجرام
    telegram_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='معرّف المستخدم في تيليجرام'
    )
    
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='معرّف المحادثة في تيليجرام'
    )
    
    telegram_username = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='اسم المستخدم في تيليجرام'
    )
    
    # الرمز
    code = models.CharField(
        max_length=6,
        verbose_name='رمز OTP'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='الحالة'
    )
    
    # الأمان
    expires_at = models.DateTimeField(
        verbose_name='تاريخ الانتهاء'
    )
    
    attempts = models.IntegerField(
        default=0,
        verbose_name='عدد المحاولات'
    )
    
    max_attempts = models.IntegerField(
        default=5,
        verbose_name='أقصى عدد محاولات'
    )
    
    # Token للرفع
    submit_token = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True,
        verbose_name='رمز التسليم'
    )
    
    submit_token_expires = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='انتهاء رمز التسليم'
    )
    
    # التوقيع
    signed_payload = models.TextField(
        verbose_name='البيانات الموقعة'
    )
    
    # IP Address
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='عنوان IP'
    )
    
    # الطوابع الزمنية
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخر تحديث'
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ التحقق'
    )
    
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ الاستخدام'
    )
    
    class Meta:
        db_table = 'project_otp'
        verbose_name = 'رمز OTP'
        verbose_name_plural = 'رموز OTP'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['submit_token']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.student_name} - {self.project.title} ({self.code})"
    
    @property
    def section(self):
        """الوصول للشعبة عبر المشروع"""
        return self.project.section
    
    def is_expired(self):
        """التحقق من انتهاء الصلاحية"""
        return timezone.now() > self.expires_at
    
    def can_verify(self):
        """التحقق من إمكانية التحقق من الرمز"""
        if self.status == 'used':
            return False, 'الرمز مستخدم بالفعل'
        
        if self.status == 'expired':
            return False, 'الرمز منتهي'
        
        if self.is_expired():
            return False, 'الرمز منتهي الصلاحية'
        
        if self.attempts >= self.max_attempts:
            return False, 'تجاوزت عدد المحاولات المسموح'
        
        return True, 'OK'
    
    def increment_attempts(self):
        """زيادة عدد المحاولات"""
        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.status = 'expired'
        self.save(update_fields=['attempts', 'status', 'updated_at'])
    
    def mark_as_verified(self):
        """تحديد كتم التحقق"""
        self.status = 'verified'
        self.verified_at = timezone.now()
        self.submit_token = secrets.token_urlsafe(32)
        self.submit_token_expires = timezone.now() + timedelta(minutes=self.project.submission_duration)
        self.save(update_fields=['status', 'verified_at', 'submit_token', 'submit_token_expires', 'updated_at'])
    
    def mark_as_used(self):
        """تحديد كمستخدم"""
        self.status = 'used'
        self.used_at = timezone.now()
        self.save(update_fields=['status', 'used_at', 'updated_at'])
    
    @staticmethod
    def generate_code():
        """توليد كود 6 أرقام"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


class OTPLog(models.Model):
    """
    سجل أحداث OTP للتتبع والتحليل
    """
    
    ACTION_CHOICES = [
        ('init', 'طلب رمز'),
        ('sent', 'إرسال رمز'),
        ('verify_attempt', 'محاولة تحقق'),
        ('verify_success', 'تحقق ناجح'),
        ('verify_failed', 'تحقق فاشل'),
        ('expired', 'انتهى'),
        ('used', 'استخدم'),
    ]
    
    otp = models.ForeignKey(
        ProjectOTP,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='OTP'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='الإجراء'
    )
    
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name='التفاصيل'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='عنوان IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='User Agent'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        db_table = 'otp_logs'
        verbose_name = 'سجل OTP'
        verbose_name_plural = 'سجلات OTP'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.otp.student_name} - {self.action}"
