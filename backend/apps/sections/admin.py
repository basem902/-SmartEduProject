"""
Django Admin Configuration for Sections App
"""
from django.contrib import admin
from .models import (
    SchoolGrade, Section, SectionLink, StudentRegistration, 
    AIGeneratedContent, TeacherJoinLink, TelegramGroup
)


@admin.register(SchoolGrade)
class SchoolGradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'teacher', 'level', 'grade_number', 'school_name', 'is_active', 'created_at']
    list_filter = ['level', 'is_active', 'created_at']
    search_fields = ['school_name', 'teacher__full_name', 'teacher__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'grade', 'section_number', 'section_name', 'total_students', 'is_active', 'created_at']
    list_filter = ['is_active', 'grade__level', 'created_at']
    search_fields = ['section_name', 'grade__school_name']
    ordering = ['grade', 'section_number']
    readonly_fields = ['total_students', 'created_at', 'updated_at']


@admin.register(SectionLink)
class SectionLinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'section', 'platform', 'view_count', 'join_count', 'is_active', 'expires_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['section__section_name', 'join_token']
    ordering = ['-created_at']
    readonly_fields = ['join_token', 'join_link', 'view_count', 'join_count', 'created_at', 'updated_at']


@admin.register(StudentRegistration)
class StudentRegistrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'grade', 'section', 'joined_telegram', 'registered_at']
    list_filter = ['joined_telegram', 'is_duplicate', 'registered_at']
    search_fields = ['full_name', 'normalized_name', 'section__section_name', 'teacher__full_name']
    ordering = ['-registered_at']
    readonly_fields = ['normalized_name', 'registered_at', 'joined_at', 'registration_ip']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher', 'grade', 'section', 'telegram_group')


@admin.register(TeacherJoinLink)
class TeacherJoinLinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'teacher', 'join_token', 'views_count', 'registrations_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['teacher__full_name', 'join_token']
    ordering = ['-created_at']
    readonly_fields = ['views_count', 'registrations_count', 'created_at', 'updated_at']


@admin.register(TelegramGroup)
class TelegramGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'section', 'group_name', 'status', 'is_bot_added', 'is_bot_admin', 'members_count', 'created_at']
    list_filter = ['status', 'is_bot_added', 'is_bot_admin', 'read_only_mode', 'created_at']
    search_fields = ['group_name', 'section__section_name', 'created_by_phone']
    ordering = ['-created_at']
    readonly_fields = ['chat_id', 'members_count', 'messages_sent', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('section', 'section__grade')


@admin.register(AIGeneratedContent)
class AIGeneratedContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'teacher', 'content_type', 'is_custom', 'model_name', 'created_at']
    list_filter = ['content_type', 'is_custom', 'model_name', 'created_at']
    search_fields = ['teacher__full_name', 'generated_text']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
