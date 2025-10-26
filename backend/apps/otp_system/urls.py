"""
URLs for OTP System
"""
from django.urls import path
from . import views

app_name = 'otp_system'

urlpatterns = [
    # OTP Management
    path('init/', views.otp_init, name='otp_init'),
    path('verify/', views.otp_verify, name='otp_verify'),
    path('check-token/', views.check_submit_token, name='check_token'),
    
    # AI Enhancement
    path('enhance/', views.enhance_text_with_ai, name='enhance_text'),
    
    # Statistics
    path('stats/', views.otp_stats, name='otp_stats'),
]
