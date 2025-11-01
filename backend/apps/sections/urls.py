"""
URLs for Sections App
"""
from django.urls import path
from . import views

app_name = 'sections'

urlpatterns = [
    # ==================== إعدادات المعلم ====================
    path('setup/', views.setup_grade, name='setup_grade'),
    path('my-grades/', views.my_grades, name='my_grades'),
    path('grade/<int:grade_id>/', views.grade_detail, name='grade_detail'),
    
    # ==================== إدارة الشُعب ====================
    path('grade/<int:grade_id>/sections/', views.grade_sections, name='grade_sections'),
    path('section/<int:section_id>/', views.section_detail, name='section_detail'),
    path('section/<int:section_id>/students/', views.section_students_list, name='section_students_list'),
    path('section/link/setup/', views.setup_section_link, name='setup_section_link'),
    path('section/<int:section_id>/link/stats/', views.section_link_stats, name='section_link_stats'),
    
    # ==================== صفحة الانضمام (Student Registration) ====================
    path('students/count/', views.get_students_count, name='get_students_count'),
    path('teacher/join-link/generate/', views.generate_teacher_join_link, name='generate_teacher_join_link'),
    path('join/<str:token>/info/', views.get_teacher_join_info, name='get_teacher_join_info'),
    path('join/<str:token>/register/', views.register_student, name='register_student'),
    
    # ==================== AI Content Generation ====================
    path('ai/generate/', views.generate_ai_content, name='generate_ai_content'),
    
    # ==================== Telegram Groups Auto-Creation ====================
    path('telegram/create-groups/', views.create_telegram_groups, name='create_telegram_groups'),
    path('telegram/create-groups-client/', views.create_telegram_groups_client, name='create_telegram_groups_client'),
    path('telegram/create-single-group/', views.create_single_telegram_group, name='create_single_telegram_group'),
    path('telegram/verify-code/', views.verify_telegram_code, name='verify_telegram_code'),
    path('telegram/apply-permissions/', views.apply_telegram_permissions, name='apply_telegram_permissions'),
    path('telegram/activate-permissions/', views.activate_group_permissions, name='activate_group_permissions'),
    
    # ==================== Telegram Session Management ====================
    path('telegram/session/login/', views.telegram_session_login, name='telegram_session_login'),
    path('telegram/session/verify/', views.telegram_session_verify, name='telegram_session_verify'),
    path('telegram/session/password/', views.telegram_session_password, name='telegram_session_password'),
    path('telegram/session/resend/', views.telegram_session_resend, name='telegram_session_resend'),
    path('telegram/session/status/', views.telegram_session_status, name='telegram_session_status'),
    path('telegram/session/disconnect/', views.telegram_session_disconnect, name='telegram_session_disconnect'),
    path('telegram/session/reset/', views.telegram_session_reset, name='telegram_session_reset'),
    
    # ==================== Telegram Groups Management (Modal-based) ====================
    path('grade/<int:grade_id>/create-telegram-groups/', views.create_telegram_groups_for_grade, name='create_telegram_groups_for_grade'),
    
    # ==================== Teacher Subjects Management ====================
    path('subjects/assign/', views.assign_subjects_to_sections, name='assign_subjects'),
    path('section/<int:section_id>/subjects/', views.get_section_subjects, name='get_section_subjects'),
    
    # ==================== Telegram Utilities ====================
    path('telegram/fix-chatid/', views.fix_telegram_chatid, name='fix_telegram_chatid'),
    path('telegram/auto-promote-bot/', views.auto_promote_bot_in_groups, name='auto_promote_bot'),
    
    # ==================== Student Join Verification ====================
    path('verify-student-join/', views.verify_student_for_join, name='verify_student_for_join'),
    path('confirm-student-joined/', views.confirm_student_joined_telegram, name='confirm_student_joined'),
    
    # ==================== Add Students (Manual / Excel) ====================
    path('students/add-manually/', views.add_students_manually, name='add_students_manually'),
    path('students/upload-excel/', views.upload_students_excel, name='upload_students_excel'),
    path('students/excel-template/', views.download_excel_template, name='download_excel_template'),
    
    # ==================== System Health ====================
    path('check-dependencies/', views.check_dependencies, name='check_dependencies'),
]
