"""
Permission decorators for Admin Panel
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User


def require_superuser(view_func):
    """
    Decorator to require superuser authentication
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response({
                'error': 'غير مصرح',
                'message': 'يجب تسجيل الدخول أولاً'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user is superuser
        if not request.user.is_superuser:
            return Response({
                'error': 'صلاحيات غير كافية',
                'message': 'هذه الصفحة مخصصة لمديري النظام فقط'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
