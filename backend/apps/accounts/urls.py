"""
URLs for Accounts App
"""
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/', views.activate, name='activate'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('subjects/', views.get_subjects, name='get_subjects'),
    path('change-password/', views.change_password, name='change_password'),
    path('settings/', views.settings, name='settings'),
]
