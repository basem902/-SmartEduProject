"""
Views for Accounts App
"""
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Teacher, TeacherPending, Settings
from .serializers import (
    RegisterSerializer, ActivateSerializer, LoginSerializer,
    ChangePasswordSerializer, TeacherSerializer, SettingsSerializer
)
from utils.security import SecurityUtils, LoginAttemptTracker, TokenManager
from utils.email import email_service
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """تسجيل معلم جديد"""
    try:
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # حذف السجلات المنتهية أولاً
        TeacherPending.objects.filter(
            email=data['email'],
            expires_at__lt=timezone.now()
        ).delete()
        
        # التحقق من وجود طلب تسجيل سابق غير منتهي
        existing = TeacherPending.objects.filter(email=data['email']).first()
        if existing:
            return Response({
                'error': 'يوجد طلب تسجيل سابق لم يتم تفعيله بعد',
                'message': 'يرجى التحقق من بريدك الإلكتروني أو الانتظار حتى انتهاء صلاحية الكود السابق'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # توليد كود التفعيل
        activation_code = SecurityUtils.generate_activation_code()
        
        # إنشاء سجل في teachers_pending
        pending = TeacherPending.objects.create(
            full_name=data['full_name'],
            email=data['email'],
            phone=data['phone'],
            school_name=data['school_name'],
            activation_code=activation_code,
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        
        # حفظ الكود في Cache
        TokenManager.store_activation_code(data['email'], activation_code, expiry_minutes=30)
        
        # إرسال إيميل التفعيل
        email_sent = email_service.send_activation_email(
            email=data['email'],
            full_name=data['full_name'],
            code=activation_code
        )
        
        logger.info(f"Registration request created for {data['email']}")
        
        return Response({
            'message': 'تم إرسال كود التفعيل إلى بريدك الإلكتروني',
            'email': data['email'],
            'code_sent': email_sent,
            'expires_in_minutes': 30
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in registration: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء التسجيل',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def activate(request):
    """تفعيل حساب المعلم"""
    try:
        serializer = ActivateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        # البحث عن الطلب
        pending = TeacherPending.objects.filter(email=email).first()
        
        if not pending:
            return Response({
                'error': 'لم يتم العثور على طلب تسجيل لهذا البريد'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # التحقق من انتهاء صلاحية الكود
        if pending.expires_at < timezone.now():
            pending.delete()
            return Response({
                'error': 'انتهت صلاحية كود التفعيل',
                'message': 'يرجى التسجيل مرة أخرى'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من الكود
        if pending.activation_code != code:
            return Response({
                'error': 'كود التفعيل غير صحيح'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # توليد كلمة مرور مؤقتة
        temp_password = SecurityUtils.generate_random_password()
        
        # إنشاء حساب User في Django
        from django.contrib.auth.models import User
        username = pending.email.split('@')[0]  # استخدام الجزء الأول من البريد كـ username
        
        # التحقق من وجود username مشابه
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=pending.email,
            password=temp_password,
            first_name=pending.full_name
        )
        
        # إنشاء حساب المعلم مرتبط بـ User
        teacher = Teacher.objects.create(
            user=user,
            full_name=pending.full_name,
            email=pending.email,
            phone=pending.phone,
            school_name=pending.school_name
        )
        teacher.set_password(temp_password)
        teacher.save()
        
        # إنشاء إعدادات افتراضية
        Settings.objects.create(teacher=teacher)
        
        # حذف الطلب المنتظر
        pending.delete()
        
        # حذف الكود من Cache
        TokenManager.delete_activation_code(email)
        
        # إرسال كلمة المرور المؤقتة
        email_sent = email_service.send_password_email(
            email=teacher.email,
            full_name=teacher.full_name,
            password=temp_password
        )
        
        logger.info(f"Account activated for {teacher.email}")
        
        return Response({
            'message': 'تم تفعيل حسابك بنجاح',
            'teacher': TeacherSerializer(teacher).data,
            'password_sent': email_sent
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in activation: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء التفعيل',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """تسجيل الدخول"""
    try:
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # التحقق من قفل الحساب
        if LoginAttemptTracker.is_account_locked(email):
            remaining = LoginAttemptTracker.get_remaining_attempts(email)
            return Response({
                'error': 'تم قفل الحساب مؤقتاً بسبب كثرة المحاولات الفاشلة',
                'message': 'يرجى المحاولة بعد ساعة'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # البحث عن المعلم
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            LoginAttemptTracker.record_failed_attempt(email)
            return Response({
                'error': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # التحقق من كلمة المرور
        if not teacher.check_password(password):
            attempts = LoginAttemptTracker.record_failed_attempt(email)
            remaining = 5 - attempts
            return Response({
                'error': 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
                'remaining_attempts': remaining
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # التحقق من تفعيل الحساب
        if not teacher.is_active:
            return Response({
                'error': 'حسابك غير مفعل',
                'message': 'يرجى التواصل مع الإدارة'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # مسح محاولات تسجيل الدخول الفاشلة
        LoginAttemptTracker.clear_attempts(email)
        
        # تحديث آخر تسجيل دخول
        teacher.last_login = timezone.now()
        teacher.save()
        
        # إنشاء JWT tokens بناءً على User
        if not teacher.user:
            # إذا لم يكن لديه user، قم بإنشاء واحد
            from django.contrib.auth.models import User
            username = teacher.email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=teacher.email,
                password=password,
                first_name=teacher.full_name
            )
            teacher.user = user
            teacher.save()
        
        refresh = RefreshToken.for_user(teacher.user)
        refresh['email'] = teacher.email
        refresh['full_name'] = teacher.full_name
        refresh['teacher_id'] = teacher.id
        
        logger.info(f"Successful login for {teacher.email}")
        
        return Response({
            'message': 'تم تسجيل الدخول بنجاح',
            'teacher': TeacherSerializer(teacher).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء تسجيل الدخول',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """الحصول على ملف المعلم الشخصي"""
    try:
        # الحصول على المعلم من الـ JWT token
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'teacher': TeacherSerializer(teacher).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subjects(request):
    """الحصول على قائمة المواد التي يدرسها المعلم"""
    try:
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # إذا لم تكن هناك مواد محددة، إرجاع قائمة افتراضية
        subjects = teacher.subjects if teacher.subjects else [
            'المهارات الرقمية',
            'العلوم',
            'الرياضيات',
            'اللغة العربية',
            'اللغة الإنجليزية',
            'الاجتماعيات',
            'التربية الإسلامية',
            'التربية الفنية',
            'التربية البدنية'
        ]
        
        return Response({
            'subjects': subjects,
            'count': len(subjects)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting subjects: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """تغيير كلمة المرور"""
    try:
        serializer = ChangePasswordSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # التحقق من كلمة المرور القديمة
        if not teacher.check_password(serializer.validated_data['old_password']):
            return Response({
                'error': 'كلمة المرور القديمة غير صحيحة'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # تعيين كلمة المرور الجديدة
        teacher.set_password(serializer.validated_data['new_password'])
        teacher.save()
        
        logger.info(f"Password changed for {teacher.email}")
        
        return Response({
            'message': 'تم تغيير كلمة المرور بنجاح'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def settings(request):
    """الحصول على/تحديث الإعدادات"""
    try:
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        settings_obj, created = Settings.objects.get_or_create(teacher=teacher)
        
        if request.method == 'GET':
            return Response({
                'settings': SettingsSerializer(settings_obj).data
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            serializer = SettingsSerializer(settings_obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return Response({
                    'error': 'بيانات غير صحيحة',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            
            logger.info(f"Settings updated for {teacher.email}")
            
            return Response({
                'message': 'تم تحديث الإعدادات بنجاح',
                'settings': serializer.data
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in settings: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
