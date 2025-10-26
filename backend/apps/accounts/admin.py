"""
Admin configuration for Accounts App
"""
from django.contrib import admin
from .models import Teacher, TeacherPending, Settings


@admin.register(TeacherPending)
class TeacherPendingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'school_name', 'activation_code', 'created_at', 'expires_at']
    search_fields = ['full_name', 'email', 'phone', 'school_name']
    list_filter = ['created_at']
    ordering = ['-created_at']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'school_name', 'is_active', 'created_at', 'last_login']
    search_fields = ['full_name', 'email', 'phone', 'school_name']
    list_filter = ['is_active', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['password_hash', 'created_at', 'updated_at', 'last_login']


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'theme', 'notifications_enabled', 'language']
    search_fields = ['teacher__full_name', 'teacher__email']
    list_filter = ['theme', 'notifications_enabled', 'language']
