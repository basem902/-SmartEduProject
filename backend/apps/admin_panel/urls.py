"""
URL configuration for Admin Panel
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    
    # Tables management
    path('tables/', views.list_tables, name='list_tables'),
    path('tables/<str:table_name>/data/', views.get_table_data_view, name='get_table_data'),
    path('tables/<str:table_name>/truncate/', views.truncate_table_view, name='truncate_table'),
    path('tables/<str:table_name>/row/<int:row_id>/', views.delete_row_view, name='delete_row'),
    path('tables/<str:table_name>/reset-sequence/', views.reset_sequence_view, name='reset_sequence'),
    
    # Database operations
    path('database/stats/', views.get_statistics, name='get_statistics'),
    path('database/wipe/', views.wipe_all_data, name='wipe_all_data'),
    
    # Teacher-specific operations
    path('teacher/<int:teacher_id>/delete-sections/', views.delete_teacher_sections_data, name='delete_teacher_sections'),
]
