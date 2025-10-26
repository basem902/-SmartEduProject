"""
Models for Projects App
"""
from django.db import models
from apps.accounts.models import Teacher


class Project(models.Model):
    """المشاريع"""
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='projects', verbose_name='المعلم')
    sections = models.ManyToManyField('sections.Section', related_name='projects', verbose_name='الشُعب')
    title = models.CharField(max_length=200, verbose_name='عنوان المشروع')
    description = models.TextField(blank=True, null=True, verbose_name='وصف المشروع')
    subject = models.CharField(max_length=100, verbose_name='المادة')
    
    # Dates
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ البداية')
    deadline = models.DateTimeField(verbose_name='آخر موعد للتسليم')
    
    # Settings
    max_file_size = models.IntegerField(default=10, verbose_name='الحد الأقصى لحجم الملف (MB)')
    allowed_file_types = models.JSONField(default=list, verbose_name='أنواع الملفات المسموحة')  # ['pdf', 'doc', etc.]
    max_grade = models.IntegerField(default=100, verbose_name='الدرجة الكاملة')
    allow_late_submission = models.BooleanField(default=False, verbose_name='السماح بالتسليم المتأخر')
    send_reminder = models.BooleanField(default=True, verbose_name='إرسال تذكير')
    ai_check_plagiarism = models.BooleanField(default=False, verbose_name='فحص الانتحال بالذكاء الاصطناعي')
    
    # Instructions
    instructions = models.TextField(blank=True, null=True, verbose_name='تعليمات المشروع')
    requirements = models.TextField(blank=True, null=True, verbose_name='شروط التسليم')
    tips = models.TextField(blank=True, null=True, verbose_name='نصائح للطلاب')
    
    # AI Generation flags
    ai_enhanced = models.BooleanField(default=False, verbose_name='محسّن بالذكاء الاصطناعي')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    telegram_sent = models.BooleanField(default=False, verbose_name='تم الإرسال للتليجرام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'مشروع'
        verbose_name_plural = 'مشاريع'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.teacher.full_name}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.deadline
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.is_expired:
            return 0
        delta = self.deadline - timezone.now()
        return delta.days


class ProjectFile(models.Model):
    """الملفات المساعدة للمشروع"""
    
    FILE_TYPE_CHOICES = [
        ('video', 'فيديو'),
        ('pdf', 'PDF'),
        ('doc', 'Office'),
        ('link', 'رابط خارجي'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files', verbose_name='المشروع')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, verbose_name='نوع الملف')
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name='مسار الملف')
    file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='اسم الملف')
    file_size = models.IntegerField(blank=True, null=True, verbose_name='حجم الملف (بايت)')
    external_link = models.URLField(max_length=500, blank=True, null=True, verbose_name='رابط خارجي')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')
    
    class Meta:
        db_table = 'project_files'
        verbose_name = 'ملف المشروع'
        verbose_name_plural = 'ملفات المشروع'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name or self.external_link} - {self.project.title}"


class Student(models.Model):
    """الطلاب"""
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='students', verbose_name='المشروع')
    student_name = models.CharField(max_length=100, verbose_name='اسم الطالب')
    student_id = models.CharField(max_length=50, verbose_name='رقم الطالب')
    phone = models.CharField(max_length=10, blank=True, null=True, verbose_name='رقم الجوال')
    email = models.EmailField(blank=True, null=True, verbose_name='البريد الإلكتروني')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')
    
    class Meta:
        db_table = 'students'
        verbose_name = 'طالب'
        verbose_name_plural = 'طلاب'
        ordering = ['student_name']
        unique_together = ['project', 'student_id']
    
    def __str__(self):
        return f"{self.student_name} ({self.student_id})"


class Group(models.Model):
    """المجموعات"""
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='groups', verbose_name='المشروع')
    group_name = models.CharField(max_length=100, verbose_name='اسم المجموعة')
    students = models.ManyToManyField(Student, related_name='groups', verbose_name='الطلاب')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        db_table = 'groups'
        verbose_name = 'مجموعة'
        verbose_name_plural = 'مجموعات'
        ordering = ['group_name']
    
    def __str__(self):
        return f"{self.group_name} - {self.project.title}"


class Submission(models.Model):
    """التسليمات"""
    
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions', verbose_name='المشروع')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='submissions', verbose_name='المجموعة')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='submissions', verbose_name='الطالب')
    file_path = models.CharField(max_length=500, verbose_name='مسار الملف')
    file_name = models.CharField(max_length=255, verbose_name='اسم الملف')
    file_size = models.IntegerField(verbose_name='حجم الملف (بايت)')
    file_type = models.CharField(max_length=50, verbose_name='نوع الملف')
    file_hash = models.CharField(max_length=64, null=True, blank=True, verbose_name='Hash الملف')
    
    # نتائج الفحص والتحقق
    validation_data = models.JSONField(null=True, blank=True, verbose_name='بيانات التحقق')
    virus_scanned = models.BooleanField(default=False, verbose_name='تم فحص الفيروسات')
    virus_clean = models.BooleanField(default=True, verbose_name='خالي من الفيروسات')
    ai_checked = models.BooleanField(default=False, verbose_name='تم الفحص بالذكاء الاصطناعي')
    ai_compliant = models.BooleanField(default=True, verbose_name='متوافق مع المتطلبات')
    ai_confidence = models.IntegerField(default=0, verbose_name='مستوى الثقة')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='الدرجة')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسليم')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ المراجعة')
    
    class Meta:
        db_table = 'submissions'
        verbose_name = 'تسليم'
        verbose_name_plural = 'تسليمات'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.project.title}"


class TelegramSendLog(models.Model):
    """سجل إرسال إشعارات Telegram"""
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='telegram_logs', verbose_name='المشروع')
    section = models.ForeignKey('sections.Section', on_delete=models.CASCADE, related_name='telegram_logs', verbose_name='الشعبة')
    success = models.BooleanField(default=False, verbose_name='نجح الإرسال')
    details = models.TextField(verbose_name='التفاصيل')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت الإرسال')
    
    class Meta:
        db_table = 'telegram_send_logs'
        verbose_name = 'سجل إرسال Telegram'
        verbose_name_plural = 'سجلات إرسال Telegram'
        ordering = ['-sent_at']
    
    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.project.title} → {self.section.section_name}"
