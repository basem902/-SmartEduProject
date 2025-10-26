"""
Views for OTP System
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import ProjectOTP, OTPLog
from .serializers import (
    OTPInitSerializer,
    OTPVerifySerializer,
    ProjectOTPSerializer,
    AIEnhanceSerializer,
    OTPStatsSerializer
)
from .utils import OTPGenerator, SignatureHelper, AIEnhancer
from apps.projects.models import Project


@api_view(['POST'])
@permission_classes([AllowAny])  # الطالب ليس لديه حساب
def otp_init(request):
    """
    طلب رمز OTP
    
    POST /api/otp/init
    {
        "project_id": 1,
        "student_name": "محمد أحمد علي",
        "payload": "p=1&sig=xxx&exp=123"
    }
    
    Returns:
    {
        "otp_id": 1,
        "bot_deeplink": "https://t.me/BotName?start=xxx",
        "expires_in": 600,
        "project_title": "بحث العلوم",
        "section_name": "شعبة 1",
        "instructions": "...",
        "requirements": "..."
    }
    """
    
    serializer = OTPInitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    project_id = serializer.validated_data['project_id']
    student_name = serializer.validated_data['student_name']
    payload = serializer.validated_data['payload']
    
    # جلب المشروع مع العلاقات
    try:
        project = Project.objects.select_related(
            'section',
            'section__link',
            'section__grade'
        ).get(id=project_id, is_active=True)
    except Project.DoesNotExist:
        return Response(
            {'error': 'المشروع غير موجود'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # التحقق من وجود شعبة
    if not project.section:
        return Response(
            {'error': 'المشروع غير مرتبط بشعبة'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # التحقق من وجود رابط تيليجرام
    try:
        section_link = project.section.link
        telegram_link = section_link.telegram_link
        
        if not telegram_link:
            raise Exception('لا يوجد رابط تيليجرام')
            
    except Exception as e:
        return Response(
            {'error': f'الشعبة لا تحتوي على رابط تيليجرام: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # التحقق من عدم وجود OTP نشط للطالب
    active_otp = ProjectOTP.objects.filter(
        project=project,
        student_name=student_name,
        status__in=['pending', 'verified'],
        expires_at__gt=timezone.now()
    ).first()
    
    if active_otp:
        # إعادة نفس المعلومات
        signed_otp_id = SignatureHelper.sign_data(str(active_otp.id))
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'YourBot')
        bot_deeplink = f"https://t.me/{bot_username}?start={signed_otp_id}"
        
        return Response({
            'otp_id': active_otp.id,
            'bot_deeplink': bot_deeplink,
            'expires_in': int((active_otp.expires_at - timezone.now()).total_seconds()),
            'project_title': project.title,
            'section_name': project.section.section_name,
            'message': 'لديك رمز نشط بالفعل'
        })
    
    # توليد كود جديد
    code = OTPGenerator.generate_code()
    expires_at = OTPGenerator.calculate_expiry(minutes=10)
    
    # الحصول على IP
    ip_address = SignatureHelper.get_client_ip(request)
    
    # إنشاء سجل OTP
    otp_record = ProjectOTP.objects.create(
        project=project,
        student_name=student_name,
        code=code,
        expires_at=expires_at,
        signed_payload=payload,
        status='pending',
        ip_address=ip_address
    )
    
    # تسجيل الحدث
    OTPLog.objects.create(
        otp=otp_record,
        action='init',
        details='طلب رمز OTP جديد',
        ip_address=ip_address,
        user_agent=SignatureHelper.get_user_agent(request)
    )
    
    # توقيع OTP ID
    signed_otp_id = SignatureHelper.sign_data(str(otp_record.id))
    
    # إنشاء deep link للبوت
    bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'YourBot')
    bot_deeplink = f"https://t.me/{bot_username}?start={signed_otp_id}"
    
    return Response({
        'otp_id': otp_record.id,
        'bot_deeplink': bot_deeplink,
        'expires_in': 600,
        'project_title': project.title,
        'section_name': project.section.section_name,
        'grade_name': project.section.grade.display_name,
        'instructions': project.instructions or 'لا توجد تعليمات',
        'requirements': project.requirements or 'لا توجد شروط',
        'submission_duration': project.submission_duration
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def otp_verify(request):
    """
    التحقق من رمز OTP
    
    POST /api/otp/verify
    {
        "otp_id": 1,
        "code": "123456"
    }
    
    Returns:
    {
        "ok": true,
        "submit_token": "xxx",
        "expires_in": 600,
        "message": "✅ تم التحقق بنجاح"
    }
    """
    
    serializer = OTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    otp_id = serializer.validated_data['otp_id']
    code = serializer.validated_data['code']
    
    # جلب السجل
    try:
        otp_record = ProjectOTP.objects.select_related('project').get(id=otp_id)
    except ProjectOTP.DoesNotExist:
        return Response(
            {'error': 'رمز غير موجود'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # التحقق من إمكانية التحقق
    can_verify, message = otp_record.can_verify()
    if not can_verify:
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # الحصول على IP
    ip_address = SignatureHelper.get_client_ip(request)
    
    # التحقق من الكود
    if otp_record.code != code:
        otp_record.increment_attempts()
        
        # تسجيل المحاولة الفاشلة
        OTPLog.objects.create(
            otp=otp_record,
            action='verify_failed',
            details=f'كود خاطئ. المحاولة {otp_record.attempts}/{otp_record.max_attempts}',
            ip_address=ip_address,
            user_agent=SignatureHelper.get_user_agent(request)
        )
        
        remaining = otp_record.max_attempts - otp_record.attempts
        return Response({
            'error': f'الرمز غير صحيح. المحاولات المتبقية: {remaining}',
            'attempts_left': remaining
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # الكود صحيح - تحديث الحالة
    otp_record.mark_as_verified()
    
    # تسجيل النجاح
    OTPLog.objects.create(
        otp=otp_record,
        action='verify_success',
        details='تم التحقق بنجاح',
        ip_address=ip_address,
        user_agent=SignatureHelper.get_user_agent(request)
    )
    
    expires_in = int((otp_record.submit_token_expires - timezone.now()).total_seconds())
    
    return Response({
        'ok': True,
        'submit_token': otp_record.submit_token,
        'expires_in': expires_in,
        'message': '✅ تم التحقق بنجاح - يمكنك الآن رفع مشروعك',
        'project_title': otp_record.project.title
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # المعلم فقط
def enhance_text_with_ai(request):
    """
    تحسين النصوص بالذكاء الاصطناعي
    
    POST /api/otp/enhance
    {
        "text": "اكتب بحث عن الطاقة",
        "type": "instructions",
        "project_id": 1
    }
    
    Returns:
    {
        "enhanced": "النص المحسن",
        "suggestions": ["اقتراح 1", "اقتراح 2"],
        "score": 88
    }
    """
    
    serializer = AIEnhanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    text = serializer.validated_data['text']
    text_type = serializer.validated_data['type']
    project_id = serializer.validated_data.get('project_id')
    
    # جلب معلومات المشروع إذا وُجد
    project_title = ''
    subject = ''
    
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
            project_title = project.title
            subject = project.subject
        except Project.DoesNotExist:
            pass
    
    # استخدام AI Enhancer
    enhancer = AIEnhancer()
    
    if text_type == 'instructions':
        result = enhancer.enhance_instructions(
            original_text=text,
            project_title=project_title,
            subject=subject
        )
        score_key = 'clarity_score'
    else:  # requirements
        result = enhancer.enhance_requirements(
            original_text=text,
            project_title=project_title
        )
        score_key = 'completeness_score'
    
    if 'error' in result:
        return Response({
            'error': result['error'],
            'enhanced': text,
            'suggestions': [],
            'score': 0
        }, status=status.HTTP_200_OK)
    
    return Response({
        'enhanced': result.get('enhanced', text),
        'suggestions': result.get('suggestions', []),
        'score': result.get(score_key, 0),
        'original': text
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def otp_stats(request):
    """
    إحصائيات OTP للمعلم
    
    GET /api/otp/stats?project_id=1
    """
    
    project_id = request.query_params.get('project_id')
    
    if project_id:
        # إحصائيات مشروع محدد
        otps = ProjectOTP.objects.filter(project_id=project_id)
    else:
        # إحصائيات جميع مشاريع المعلم
        teacher = request.user.teacher_profile
        otps = ProjectOTP.objects.filter(project__teacher=teacher)
    
    total = otps.count()
    if total == 0:
        return Response({
            'total_requests': 0,
            'verified_count': 0,
            'expired_count': 0,
            'used_count': 0,
            'pending_count': 0,
            'average_attempts': 0,
            'success_rate': 0
        })
    
    verified = otps.filter(status='verified').count()
    expired = otps.filter(status='expired').count()
    used = otps.filter(status='used').count()
    pending = otps.filter(status='pending').count()
    
    # متوسط المحاولات
    avg_attempts = otps.aggregate(avg=models.Avg('attempts'))['avg'] or 0
    
    # نسبة النجاح
    success_rate = (verified + used) / total * 100 if total > 0 else 0
    
    stats = {
        'total_requests': total,
        'verified_count': verified,
        'expired_count': expired,
        'used_count': used,
        'pending_count': pending,
        'average_attempts': round(avg_attempts, 2),
        'success_rate': round(success_rate, 2)
    }
    
    serializer = OTPStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_submit_token(request):
    """
    التحقق من صلاحية submit_token
    
    GET /api/otp/check-token?token=xxx
    """
    
    submit_token = request.query_params.get('token')
    if not submit_token:
        return Response(
            {'valid': False, 'error': 'الرمز مطلوب'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        otp_record = ProjectOTP.objects.get(
            submit_token=submit_token,
            status='verified',
            submit_token_expires__gt=timezone.now()
        )
        
        expires_in = int((otp_record.submit_token_expires - timezone.now()).total_seconds())
        
        return Response({
            'valid': True,
            'expires_in': expires_in,
            'student_name': otp_record.student_name,
            'project_title': otp_record.project.title
        })
        
    except ProjectOTP.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'رمز غير صالح أو منتهي'
        })


# استيراد models للـ stats
from django.db import models
