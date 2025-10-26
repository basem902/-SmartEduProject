"""
URLs for Projects App
"""
from django.urls import path
from . import views
from . import views_create
from . import views_project_new
from . import views_ai
from . import views_telegram
from . import views_test

urlpatterns = [
    # 🧪 TEST Endpoint - Save to JSON file
    path('test-create/', views_test.test_project_create, name='test_project_create'),
    
    # AI Content Generation
    path('ai/generate/', views_ai.generate_project_content, name='generate_project_ai'),
    
    # New Project Creation (V2 - Clean)
    path('create-new/', views_project_new.create_project_v2, name='create_project_v2'),
    
    # Old Project Creation (keep for fallback)
    path('create/', views_create.create_project, name='create_project'),
    path('list/', views_create.list_projects, name='list_projects'),
    path('<int:project_id>/detail/', views_create.project_detail, name='project_detail_new'),
    path('<int:project_id>/delete/', views_create.delete_project, name='delete_project'),
    
    # Old URLs (keep for compatibility)
    path('', views.project_list_create, name='project_list_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:project_id>/students/', views.student_list_create, name='student_list_create'),
    path('<int:project_id>/submissions/', views.submission_list, name='submission_list'),
    path('<int:project_id>/validate/', views.validate_file, name='validate_file'),
    path('submissions/upload/', views.upload_submission, name='upload_submission'),
    path('submissions/<int:submission_id>/review/', views.review_submission, name='review_submission'),
    
    # Telegram Notifications
    path('<int:project_id>/send-telegram/', views.send_project_telegram, name='send_project_telegram'),
    path('<int:project_id>/telegram/bot-status/', views_telegram.check_bot_status, name='check_bot_status'),
]
