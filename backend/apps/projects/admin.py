"""
Admin configuration for Projects App
"""
from django.contrib import admin
from .models import Project, ProjectFile, Student, Group, Submission


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'subject', 'start_date', 'deadline', 'telegram_sent', 'is_active', 'created_at']
    search_fields = ['title', 'teacher__full_name', 'subject']
    list_filter = ['is_active', 'subject', 'telegram_sent', 'ai_enhanced', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'telegram_sent']
    filter_horizontal = ['sections']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'student_id', 'project', 'phone', 'email', 'created_at']
    search_fields = ['student_name', 'student_id', 'phone', 'email']
    list_filter = ['project', 'created_at']
    ordering = ['student_name']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'project', 'created_at']
    search_fields = ['group_name', 'project__title']
    list_filter = ['project', 'created_at']
    ordering = ['group_name']
    filter_horizontal = ['students']


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'project', 'file_type', 'file_size', 'uploaded_at']
    search_fields = ['file_name', 'project__title', 'external_link']
    list_filter = ['file_type', 'uploaded_at', 'project']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'project', 'student', 'group', 'status', 'grade', 'submitted_at']
    search_fields = ['file_name', 'project__title', 'student__student_name']
    list_filter = ['status', 'submitted_at', 'project']
    ordering = ['-submitted_at']
    readonly_fields = ['file_path', 'file_size', 'file_type', 'submitted_at']
