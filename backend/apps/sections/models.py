"""
Models for Sections Management (الصفوف والشُعب)
"""
from django.db import models
from apps.accounts.models import Teacher
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
import json


class SchoolGrade(models.Model):
    """المراحل والصفوف الدراسية"""
    
    LEVEL_CHOICES = [
        ('elementary', 'ابتدائي'),
        ('middle', 'متوسط'),
        ('high', 'ثانوي'),
    ]
    
    GRADE_CHOICES = {
        'elementary': [(i, f'الصف {i}') for i in range(1, 7)],  # 1-6
        'middle': [(i, f'الصف {i}') for i in range(1, 4)],      # 1-3
        'high': [(i, f'الصف {i}') for i in range(1, 4)],        # 1-3
    }
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='grades', verbose_name='المعلم')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name='المرحلة')
    grade_number = models.IntegerField(verbose_name='رقم الصف')
    school_name = models.CharField(max_length=200, verbose_name='اسم المدرسة')
    subject = models.CharField(max_length=100, default='غير محدد', verbose_name='المادة الدراسية', help_text='مثال: المهارات الرقمية، الرياضيات، العلوم')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    
    class Meta:
        db_table = 'school_grades'
        verbose_name = 'صف دراسي'
        verbose_name_plural = 'صفوف دراسية'
        unique_together = ['teacher', 'level', 'grade_number', 'subject']  # السماح بنفس الصف لمواد مختلفة
        ordering = ['level', 'grade_number']
    
    def __str__(self):
        level_display = dict(self.LEVEL_CHOICES)[self.level]
        return f"{self.school_name} - {level_display} - الصف {self.grade_number} - {self.subject}"
    
    @property
    def display_name(self):
        level_display = dict(self.LEVEL_CHOICES)[self.level]
        return f"{level_display} - الصف {self.grade_number} - {self.subject}"


class Section(models.Model):
    """الشُعب الدراسية"""
    
    grade = models.ForeignKey(SchoolGrade, on_delete=models.CASCADE, related_name='sections', verbose_name='الصف')
    section_number = models.IntegerField(verbose_name='رقم الشعبة')
    section_name = models.CharField(max_length=50, verbose_name='اسم الشعبة')  # "شعبة 1"
    total_students = models.IntegerField(default=0, verbose_name='عدد الطلاب')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    
    class Meta:
        db_table = 'sections'
        verbose_name = 'شعبة'
        verbose_name_plural = 'شُعب'
        unique_together = ['grade', 'section_number']
        ordering = ['grade', 'section_number']
    
    def __str__(self):
        return f"{self.grade.display_name} - {self.section_name}"
    
    def update_student_count(self):
        """تحديث عدد الطلاب"""
        self.total_students = self.registered_students.count()
        self.save()


class SectionLink(models.Model):
    """روابط قروبات الشُعب"""
    
    PLATFORM_CHOICES = [
        ('whatsapp', 'واتساب'),
        ('telegram', 'تيليجرام'),
        ('both', 'كلاهما'),
    ]
    
    section = models.OneToOneField(Section, on_delete=models.CASCADE, related_name='link', verbose_name='الشعبة')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='whatsapp', verbose_name='المنصة')
    whatsapp_link = models.URLField(blank=True, null=True, verbose_name='رابط واتساب')
    telegram_link = models.URLField(blank=True, null=True, verbose_name='رابط تيليجرام')
    
    # الرابط الذكي المولد
    join_token = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='رمز الانضمام')
    join_link = models.CharField(max_length=500, verbose_name='رابط الانضمام')
    
    # الصلاحية
    expires_at = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    # إحصائيات
    view_count = models.IntegerField(default=0, verbose_name='عدد المشاهدات')
    join_count = models.IntegerField(default=0, verbose_name='عدد الانضمامات')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    
    class Meta:
        db_table = 'section_links'
        verbose_name = 'رابط شعبة'
        verbose_name_plural = 'روابط الشُعب'
    
    def __str__(self):
        return f"رابط {self.section.section_name}"
    
    def save(self, *args, **kwargs):
        if not self.join_token:
            self.join_token = self.generate_token()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=90)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_token():
        """توليد رمز آمن"""
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        """التحقق من انتهاء الصلاحية"""
        return timezone.now() > self.expires_at
    
    def increment_views(self):
        """زيادة عدد المشاهدات"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_joins(self):
        """زيادة عدد الانضمامات"""
        self.join_count += 1
        self.save(update_fields=['join_count'])


class AIGeneratedContent(models.Model):
    """المحتوى المُولد بالذكاء الاصطناعي"""
    
    CONTENT_TYPES = [
        ('instructions', 'تعليمات الاستلام'),
        ('benefits', 'فوائد النظام'),
        ('welcome', 'رسالة ترحيب'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='ai_content', verbose_name='المعلم')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name='نوع المحتوى')
    generated_text = models.TextField(verbose_name='النص المُولد')
    is_custom = models.BooleanField(default=False, verbose_name='معدّل يدوياً')
    
    # معلومات التوليد
    prompt_used = models.TextField(blank=True, verbose_name='Prompt المستخدم')
    model_name = models.CharField(max_length=50, default='gemini-pro', verbose_name='اسم النموذج')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التوليد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تعديل')
    
    class Meta:
        db_table = 'ai_generated_content'
        verbose_name = 'محتوى AI'
        verbose_name_plural = 'محتوى AI'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{dict(self.CONTENT_TYPES)[self.content_type]} - {self.teacher.full_name}"


class TelegramGroup(models.Model):
    """قروبات تيليجرام المرتبطة بالشُعب"""
    
    STATUS_CHOICES = [
        ('pending', 'قيد الإنشاء'),
        ('created', 'تم الإنشاء'),
        ('bot_added', 'تم إضافة البوت'),
        ('bot_admin', 'البوت مدير'),
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('error', 'خطأ'),
    ]
    
    section = models.OneToOneField(
        Section,
        on_delete=models.CASCADE,
        related_name='telegram_group',
        verbose_name='الشعبة'
    )
    
    # معلومات القروب
    group_name = models.CharField(max_length=200, verbose_name='اسم القروب')
    chat_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name='Telegram Chat ID')
    invite_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='رابط الانضمام')
    
    # حالة البوت
    bot_username = models.CharField(max_length=100, default='SmartEduProjectBot', verbose_name='اسم البوت')
    is_bot_added = models.BooleanField(default=False, verbose_name='هل البوت مضاف؟')
    is_bot_admin = models.BooleanField(default=False, verbose_name='هل البوت مدير؟')
    bot_permissions = models.JSONField(default=dict, blank=True, verbose_name='صلاحيات البوت')
    
    # صلاحيات القروب
    permissions_applied = models.BooleanField(default=False, verbose_name='هل الصلاحيات مطبقة؟')
    read_only_mode = models.BooleanField(default=True, verbose_name='وضع القراءة فقط')
    
    # رسالة التعليمات
    instructions_message_id = models.BigIntegerField(null=True, blank=True, verbose_name='معرف رسالة التعليمات')
    instructions_sent = models.BooleanField(default=False, verbose_name='هل تم إرسال التعليمات؟')
    instructions_pinned = models.BooleanField(default=False, verbose_name='هل تم تثبيت التعليمات؟')
    
    # حالة القروب
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='الحالة'
    )
    error_message = models.TextField(blank=True, verbose_name='رسالة الخطأ')
    
    # إحصائيات
    members_count = models.IntegerField(default=0, verbose_name='عدد الأعضاء')
    messages_sent = models.IntegerField(default=0, verbose_name='عدد الرسائل المرسلة')
    last_message_at = models.DateTimeField(null=True, blank=True, verbose_name='آخر رسالة')
    
    # معلومات الإنشاء
    created_by_phone = models.CharField(max_length=20, verbose_name='رقم هاتف المنشئ')
    creation_metadata = models.JSONField(default=dict, blank=True, verbose_name='بيانات إضافية')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    
    class Meta:
        db_table = 'telegram_groups'
        verbose_name = 'قروب تيليجرام'
        verbose_name_plural = 'قروبات تيليجرام'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.group_name} ({self.get_status_display()})"
    
    @property
    def is_fully_configured(self):
        """هل القروب مكتمل الإعداد؟"""
        return (
            self.is_bot_added and
            self.is_bot_admin and
            self.permissions_applied and
            self.instructions_sent and
            self.status == 'active'
        )
    
    def update_status(self):
        """تحديث الحالة تلقائياً بناءً على المعلومات"""
        if self.is_fully_configured:
            self.status = 'active'
        elif self.is_bot_admin:
            self.status = 'bot_admin'
        elif self.is_bot_added:
            self.status = 'bot_added'
        elif self.chat_id:
            self.status = 'created'
        else:
            self.status = 'pending'
        self.save()


class TeacherJoinLink(models.Model):
    """رابط انضمام الطلاب الخاص بكل معلم"""
    
    teacher = models.OneToOneField(
        'accounts.Teacher',
        on_delete=models.CASCADE,
        related_name='join_link',
        verbose_name='المعلم'
    )
    
    # الرابط الفريد
    join_token = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='رمز الرابط')
    join_url = models.CharField(max_length=500, verbose_name='رابط الانضمام')
    
    # 🔐 كلمة المرور (اختيارية)
    password = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        default=None,
        verbose_name='كلمة المرور',
        help_text='كلمة مرور اختيارية لحماية رابط الانضمام'
    )
    
    # إحصائيات
    views_count = models.IntegerField(default=0, verbose_name='عدد المشاهدات')
    registrations_count = models.IntegerField(default=0, verbose_name='عدد التسجيلات')
    
    # حالة الرابط
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    
    class Meta:
        db_table = 'teacher_join_links'
        verbose_name = 'رابط انضمام المعلم'
        verbose_name_plural = 'روابط انضمام المعلمين'
    
    def __str__(self):
        return f"رابط {self.teacher.username}"


class StudentRegistration(models.Model):
    """تسجيل الطلاب في القروبات"""
    
    # البيانات الشخصية
    full_name = models.CharField(max_length=200, verbose_name='الاسم الكامل')
    normalized_name = models.CharField(max_length=200, db_index=True, verbose_name='الاسم المعياري')
    
    # معلومات التليجرام
    telegram_user_id = models.BigIntegerField(null=True, blank=True, unique=True, verbose_name='Telegram User ID')
    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram Username')
    
    # الربط بالمعلم والمدرسة
    teacher = models.ForeignKey(
        'accounts.Teacher',
        on_delete=models.CASCADE,
        related_name='registered_students',
        verbose_name='المعلم'
    )
    school_name = models.CharField(max_length=200, verbose_name='اسم المدرسة')
    
    # الربط بالصف والشعبة
    grade = models.ForeignKey(
        SchoolGrade,
        on_delete=models.CASCADE,
        related_name='registered_students',
        verbose_name='الصف'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='registered_students',
        verbose_name='الشعبة'
    )
    
    # الربط بقروب التليجرام
    telegram_group = models.ForeignKey(
        TelegramGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_students',
        verbose_name='قروب التليجرام'
    )
    telegram_invite_link = models.URLField(blank=True, null=True, default='', verbose_name='رابط القروب')
    
    # معلومات التسجيل
    registration_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP المستخدم')
    user_agent = models.TextField(blank=True, verbose_name='معلومات المتصفح')
    
    # حالة الانضمام
    joined_telegram = models.BooleanField(default=False, verbose_name='انضم للتليجرام')
    joined_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الانضمام')
    
    # التكرار
    is_duplicate = models.BooleanField(default=False, verbose_name='تسجيل مكرر')
    original_name = models.CharField(max_length=200, blank=True, verbose_name='الاسم الأصلي')
    
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')
    
    class Meta:
        db_table = 'student_registrations'
        verbose_name = 'تسجيل طالب'
        verbose_name_plural = 'تسجيلات الطلاب'
        ordering = ['-registered_at']
        unique_together = [['teacher', 'grade', 'section', 'normalized_name']]
        indexes = [
            models.Index(fields=['teacher', 'grade', 'section', 'normalized_name']),
            models.Index(fields=['telegram_group']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.section.section_name}"


class TeacherSubject(models.Model):
    """المواد التي يدرسها المعلم لكل صف/شعبة"""
    
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='teaching_subjects',
        verbose_name='المعلم'
    )
    teacher_phone = models.CharField(max_length=10, verbose_name='رقم جوال المعلم')
    
    subject_name = models.CharField(max_length=100, verbose_name='اسم المادة')
    
    grade = models.ForeignKey(
        SchoolGrade,
        on_delete=models.CASCADE,
        related_name='teacher_subjects',
        verbose_name='الصف'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='teacher_subjects',
        verbose_name='الشعبة'
    )
    
    # معلومات إضافية
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    
    class Meta:
        db_table = 'teacher_subjects'
        verbose_name = 'مادة معلم'
        verbose_name_plural = 'مواد المعلمين'
        unique_together = ['teacher', 'subject_name', 'grade', 'section']
        ordering = ['grade', 'section', 'subject_name']
        indexes = [
            models.Index(fields=['teacher', 'grade', 'section']),
            models.Index(fields=['subject_name']),
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.subject_name} - {self.section.section_name}"
    
    def save(self, *args, **kwargs):
        # Auto-fill teacher_phone from teacher
        if not self.teacher_phone:
            self.teacher_phone = self.teacher.phone
        super().save(*args, **kwargs)
