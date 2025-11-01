"""
Views for Sections Management
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from .models import SchoolGrade, Section, SectionLink, StudentRegistration, AIGeneratedContent, TelegramGroup, TeacherSubject
from apps.accounts.models import Teacher
from .serializers import (
    SchoolGradeSerializer, SectionSerializer, SectionDetailSerializer,
    SectionLinkSerializer, StudentRegistrationSerializer,
    AIGeneratedContentSerializer, GradeSetupSerializer,
    SectionLinkSetupSerializer, StudentJoinSerializer, AIGenerateSerializer,
    TelegramGroupSerializer, CreateTelegramGroupsSerializer,
    TeacherSubjectSerializer, AssignSubjectsSerializer
)
from .utils import (
    LinkGenerator, LinkValidator, IPHelper, StatsCalculator,
    NameCleaner, SectionHelper
)
import logging

logger = logging.getLogger(__name__)


def normalize_telegram_chatid(chat_id):
    """
    تحويل chat_id إلى الصيغة الصحيحة (سالب مع -100 prefix)
    
    Examples:
        3298260616 → -1003298260616
        -1003298260616 → -1003298260616 (no change)
    """
    if chat_id is None:
        return None
    
    chat_id = int(chat_id)
    
    # إذا كان سالباً بالفعل، لا تغيير
    if chat_id < 0:
        return chat_id
    
    # إذا كان موجباً، حوله لسالب مع -100 prefix
    # Formula: -(1000000000000 + chat_id)
    return -(1000000000000 + chat_id)


# ==================== إعدادات المعلم ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_grade(request):
    """إنشاء صف مع شُعبه"""
    try:
        # الحصول على المعلم
        teacher = get_teacher_from_request(request)
        
        serializer = GradeSetupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        with transaction.atomic():
            # إنشاء أو استرجاع الصف (لتجنب خطأ التكرار)
            grade, grade_created = SchoolGrade.objects.get_or_create(
                teacher=teacher,
                level=data['level'],
                grade_number=data['grade_number'],
                subject=data.get('subject', 'غير محدد'),
                defaults={
                    'school_name': NameCleaner.normalize_school_name(data['school_name']),
                    'is_active': True
                }
            )
            
            # إذا كان الصف موجوداً، تحديث اسم المدرسة
            if not grade_created:
                grade.school_name = NameCleaner.normalize_school_name(data['school_name'])
                grade.is_active = True
                grade.save(update_fields=['school_name', 'is_active'])
                logger.info(f"Grade {grade.id} already exists, updated school_name by {teacher.email}")
            else:
                logger.info(f"Grade {grade.id} newly created by {teacher.email}")
            
            # حفظ المادة في Teacher.subjects إذا لم تكن موجودة
            if 'subject' in data and data['subject']:
                teacher_subjects = teacher.subjects or []
                if data['subject'] not in teacher_subjects:
                    teacher_subjects.append(data['subject'])
                    teacher.subjects = teacher_subjects
                    teacher.save(update_fields=['subjects'])
            
            # إنشاء الشُعب فقط إذا لم تكن موجودة
            existing_sections = grade.sections.all()
            
            if existing_sections.exists():
                # الصف موجود والشُعب موجودة - لا نفعل شيء
                sections = list(existing_sections)
                logger.info(f"Grade {grade.id} has {len(sections)} existing sections")
            else:
                # إنشاء الشُعب
                # إذا تم إرسال قائمة الشُعب المختارة، استخدمها
                if 'sections_list' in data and data['sections_list']:
                    sections = SectionHelper.create_sections_from_list(grade, data['sections_list'])
                    logger.info(f"Grade {grade.id} created with {len(sections)} selected sections: {data['sections_list']} by {teacher.email}")
                # وإلا أنشئ الشُعب تلقائياً حسب العدد
                else:
                    sections = SectionHelper.bulk_create_sections(grade, data['sections_count'])
                    logger.info(f"Grade {grade.id} created with {len(sections)} auto-generated sections by {teacher.email}")
        
        message = 'تم إنشاء الصف والشُعب بنجاح' if grade_created else 'الصف موجود مسبقاً'
        status_code = status.HTTP_201_CREATED if grade_created else status.HTTP_200_OK
        
        return Response({
            'message': message,
            'grade': SchoolGradeSerializer(grade).data,
            'sections_count': len(sections),
            'is_new': grade_created
        }, status=status_code)
        
    except Exception as e:
        logger.error(f"Error in setup_grade: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء الإنشاء',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_grades(request):
    """جلب جميع صفوف المعلم"""
    try:
        teacher = get_teacher_from_request(request)
        
        grades = SchoolGrade.objects.filter(
            teacher=teacher,
            is_active=True
        ).prefetch_related('sections')
        
        serializer = SchoolGradeSerializer(grades, many=True)
        
        # إحصائيات عامة
        stats = StatsCalculator.calculate_teacher_stats(teacher)
        
        return Response({
            'grades': serializer.data,
            'stats': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in my_grades: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def grade_detail(request, grade_id):
    """تفاصيل/تعديل/حذف صف"""
    try:
        teacher = get_teacher_from_request(request)
        grade = get_object_or_404(SchoolGrade, id=grade_id, teacher=teacher)
        
        if request.method == 'GET':
            serializer = SchoolGradeSerializer(grade)
            stats = StatsCalculator.calculate_grade_stats(grade)
            
            return Response({
                'grade': serializer.data,
                'stats': stats
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            # تعديل بيانات الصف
            if 'school_name' in request.data:
                grade.school_name = NameCleaner.normalize_school_name(request.data['school_name'])
            if 'is_active' in request.data:
                grade.is_active = request.data['is_active']
            
            grade.save()
            
            return Response({
                'message': 'تم التحديث بنجاح',
                'grade': SchoolGradeSerializer(grade).data
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            grade.delete()
            return Response({
                'message': 'تم حذف الصف بنجاح'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in grade_detail: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== إدارة الشُعب ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def grade_sections(request, grade_id):
    """جلب شُعب صف معين"""
    try:
        teacher = get_teacher_from_request(request)
        grade = get_object_or_404(SchoolGrade, id=grade_id, teacher=teacher)
        
        # استخدام all() بدلاً من filter لأن الشُعب الجديدة قد لا تحتوي link
        sections = grade.sections.all().select_related('grade').prefetch_related('registered_students')
        
        serializer = SectionSerializer(sections, many=True)
        
        return Response({
            'sections': serializer.data,
            'grade': SchoolGradeSerializer(grade).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in grade_sections for grade {grade_id}: {str(e)}", exc_info=True)
        return Response({
            'error': 'حدث خطأ في جلب الشُعب',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def section_detail(request, section_id):
    """تفاصيل شعبة مع الطلاب"""
    try:
        teacher = get_teacher_from_request(request)
        section = get_object_or_404(
            Section.objects.select_related('grade'),
            id=section_id,
            grade__teacher=teacher
        )
        
        serializer = SectionDetailSerializer(section)
        stats = StatsCalculator.calculate_section_stats(section)
        
        return Response({
            'section': serializer.data,
            'stats': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in section_detail: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def section_students_list(request, section_id):
    """قائمة الطلاب المسجلين في شعبة"""
    try:
        teacher = get_teacher_from_request(request)
        
        # التحقق من ملكية الشعبة
        section = get_object_or_404(
            Section,
            id=section_id,
            grade__teacher=teacher
        )
        
        # جلب جميع الطلاب المسجلين
        students = StudentRegistration.objects.filter(
            section=section
        ).order_by('-registered_at')
        
        # الإحصائيات
        total_registered = students.count()
        joined_telegram = students.filter(joined_telegram=True).count()
        not_joined = total_registered - joined_telegram
        
        # آخر تسجيل
        last_registration = students.first()
        last_registration_time = last_registration.registered_at if last_registration else None
        
        # تجهيز البيانات
        students_data = []
        for idx, student in enumerate(students, 1):
            students_data.append({
                'id': student.id,
                'number': idx,
                'full_name': student.full_name,
                'joined_telegram': student.joined_telegram,
                'registered_at': student.registered_at,
                'joined_at': student.joined_at,
                'registration_ip': student.registration_ip
            })
        
        return Response({
            'section': {
                'id': section.id,
                'name': section.section_name,
                'grade': section.grade.display_name
            },
            'statistics': {
                'total_registered': total_registered,
                'joined_telegram': joined_telegram,
                'not_joined': not_joined
            },
            'students': students_data,
            'last_registration': last_registration_time
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in section_students_list: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_section_link(request):
    """إعداد روابط شعبة"""
    try:
        teacher = get_teacher_from_request(request)
        
        serializer = SectionLinkSetupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # التحقق من ملكية الشعبة
        section = get_object_or_404(
            Section,
            id=data['section_id'],
            grade__teacher=teacher
        )
        
        # فحص الروابط
        is_valid, errors = LinkValidator.validate_platform_links(
            data['platform'],
            data.get('whatsapp_link'),
            data.get('telegram_link')
        )
        
        if not is_valid:
            return Response({
                'error': 'روابط غير صحيحة',
                'details': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # إنشاء أو تحديث الرابط
            link, created = SectionLink.objects.get_or_create(section=section)
            
            link.platform = data['platform']
            link.whatsapp_link = data.get('whatsapp_link')
            link.telegram_link = data.get('telegram_link')
            
            # توليد الرابط الذكي
            if not link.join_token:
                link.join_token = LinkGenerator.generate_join_token()
            
            link.join_link = LinkGenerator.generate_join_link(
                section.id,
                link.join_token,
                request
            )
            
            link.save()
            
            logger.info(f"Section link {link.id} {'created' if created else 'updated'} by {teacher.email}")
            
            # ✅ حفظ في TelegramGroup أيضاً (إذا كان telegram)
            if data['platform'] == 'telegram' and data.get('telegram_link'):
                telegram_link = data.get('telegram_link')
                chat_id = data.get('chat_id')  # ✅ استقبال chat_id من Frontend
                
                # ✅ تحويل chat_id إلى سالب تلقائياً
                normalized_chat_id = normalize_telegram_chatid(chat_id)
                
                logger.info(f"Original chat_id: {chat_id}, Normalized: {normalized_chat_id}")
                
                # إنشاء أو تحديث TelegramGroup
                telegram_group, tg_created = TelegramGroup.objects.get_or_create(
                    section=section,
                    defaults={
                        'group_name': f"{section.grade.display_name} - {section.section_name}",
                        'invite_link': telegram_link,
                        'chat_id': normalized_chat_id,  # ✅ حفظ chat_id سالب
                        'created_by_phone': teacher.phone or 'unknown',
                        'status': 'active',
                        'is_bot_added': False,  # لم يتم إضافة البوت بعد
                        'creation_metadata': {
                            'created_from': 'setup_section_link',
                            'created_at': timezone.now().isoformat()
                        }
                    }
                )
                
                # تحديث السجل الموجود
                if not tg_created:
                    telegram_group.invite_link = telegram_link
                    telegram_group.chat_id = normalized_chat_id  # ✅ تحديث chat_id سالب
                    telegram_group.group_name = f"{section.grade.display_name} - {section.section_name}"
                    telegram_group.status = 'active'
                    telegram_group.save()
                    logger.info(f"Updated existing TelegramGroup {telegram_group.id} for section {section.id}")
                else:
                    logger.info(f"Created new TelegramGroup {telegram_group.id} for section {section.id}")
        
        return Response({
            'message': 'تم إعداد الرابط بنجاح',
            'link': SectionLinkSerializer(link).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in setup_section_link: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def section_link_stats(request, section_id):
    """إحصائيات رابط الشعبة"""
    try:
        teacher = get_teacher_from_request(request)
        section = get_object_or_404(
            Section,
            id=section_id,
            grade__teacher=teacher
        )
        
        if not hasattr(section, 'link'):
            return Response({
                'error': 'لم يتم إنشاء رابط لهذه الشعبة بعد'
            }, status=status.HTTP_404_NOT_FOUND)
        
        link = section.link
        stats = {
            'views': link.view_count,
            'joins': link.join_count,
            'join_rate': (link.join_count / link.view_count * 100) if link.view_count > 0 else 0,
            'is_expired': link.is_expired(),
            'expires_at': link.expires_at,
            'link': link.join_link
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in section_link_stats: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== صفحة الانضمام (Join Page) ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def join_page_info(request, token):
    """معلومات الشعبة للطالب"""
    try:
        # البحث عن الرابط
        link = get_object_or_404(SectionLink, join_token=token, is_active=True)
        
        # التحقق من الصلاحية
        if link.is_expired():
            return Response({
                'error': 'انتهت صلاحية هذا الرابط',
                'message': 'يرجى التواصل مع المعلم للحصول على رابط جديد'
            }, status=status.HTTP_410_GONE)
        
        # زيادة عدد المشاهدات
        link.increment_views()
        
        section = link.section
        grade = section.grade
        
        # جلب محتوى AI إن وجد
        ai_content = {}
        for content_type in ['instructions', 'benefits', 'welcome']:
            content = AIGeneratedContent.objects.filter(
                teacher=grade.teacher,
                content_type=content_type
            ).first()
            if content:
                ai_content[content_type] = content.generated_text
        
        return Response({
            'section': {
                'name': section.section_name,
                'grade': grade.display_name,
                'school': grade.school_name
            },
            'teacher': {
                'name': grade.teacher.full_name
            },
            'platform': {
                'type': link.platform,
                'whatsapp': link.whatsapp_link,
                'telegram': link.telegram_link
            },
            'content': ai_content,
            'token': token
        }, status=status.HTTP_200_OK)
        
    except SectionLink.DoesNotExist:
        return Response({
            'error': 'رابط غير صحيح',
            'message': 'تأكد من صحة الرابط'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in join_page_info: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== AI Content Generation ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_ai_content(request):
    """توليد محتوى بالذكاء الاصطناعي"""
    try:
        teacher = get_teacher_from_request(request)
        
        serializer = AIGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        content_type = data['content_type']
        
        # تجهيز السياق
        context = {
            'school_name': data.get('school_name', ''),
            'grade': data.get('grade_level', ''),
            'section': data.get('section_name', ''),
            'student_name': data.get('context', {}).get('student_name', '')
        }
        
        # توليد المحتوى
        from utils.ai_service import ai_generator
        
        if content_type == 'instructions':
            generated_text = ai_generator.generate_instructions(context)
        elif content_type == 'benefits':
            generated_text = ai_generator.generate_benefits(context)
        elif content_type == 'welcome':
            generated_text = ai_generator.generate_welcome(context)
        else:
            return Response({
                'error': 'نوع محتوى غير صحيح'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # حفظ في قاعدة البيانات
        ai_content = AIGeneratedContent.objects.create(
            teacher=teacher,
            content_type=content_type,
            generated_text=generated_text,
            prompt_used=str(context),
            model_name='default'
        )
        
        return Response({
            'message': 'تم توليد المحتوى بنجاح',
            'content': AIGeneratedContentSerializer(ai_content).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in generate_ai_content: {str(e)}")
        return Response({
            'error': 'حدث خطأ في التوليد',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Helper Functions ====================

def get_teacher_from_request(request):
    """الحصول على المعلم من الـ request"""
    if hasattr(request.user, 'teacher_profile'):
        return request.user.teacher_profile
    
    # البحث بالبريد من JWT
    email = request.user.email
    teacher = Teacher.objects.filter(email=email).first()
    
    if not teacher:
        # إنشاء Teacher تلقائياً للـ User الجديد
        logger.warning(f"Teacher not found for {email}. Creating automatically...")
        
        # استخراج الاسم من البريد
        name = email.split('@')[0]
        
        teacher = Teacher.objects.create(
            user=request.user,
            email=email,
            full_name=name,
            phone="0000000000",  # رقم مؤقت
            school_name="غير محدد",
            password_hash="auto_generated",
            is_active=True
        )
        
        logger.info(f"Auto-created Teacher (id={teacher.id}) for user {email}")
    
    return teacher


# ==================== إنشاء قروبات تيليجرام تلقائياً ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_telegram_groups(request):
    """
    إنشاء قروبات تيليجرام تلقائياً للشُعب
    
    Request Body:
    {
        "grade_name": "الصف الثالث",
        "subject_name": "المهارات الرقمية",
        "sections": ["أ", "ب", "ج"]
    }
    """
    try:
        # الحصول على المعلم
        teacher = get_teacher_from_request(request)
        
        # التحقق من وجود telegram_id
        if not teacher.telegram_id:
            return Response({
                'error': 'معرف تيليجرام غير موجود',
                'message': 'يجب إضافة معرف تيليجرام الخاص بك في الإعدادات أولاً'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على البيانات
        grade_name = request.data.get('grade_name')
        subject_name = request.data.get('subject_name')
        sections = request.data.get('sections', [])
        
        # التحقق من البيانات
        if not grade_name or not subject_name or not sections:
            return Response({
                'error': 'بيانات ناقصة',
                'message': 'يجب توفير اسم الصف، اسم المادة، وقائمة الشُعب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(sections, list) or len(sections) == 0:
            return Response({
                'error': 'قائمة الشُعب غير صحيحة',
                'message': 'يجب أن تكون قائمة الشُعب غير فارغة'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # استيراد الـ Helper
        from .telegram_groups import create_telegram_groups_sync
        
        # إنشاء القروبات
        logger.info(f"Creating {len(sections)} Telegram groups for teacher {teacher.id}")
        
        results = create_telegram_groups_sync(
            grade_name=grade_name,
            subject_name=subject_name,
            sections=sections,
            teacher_telegram_id=teacher.telegram_id,
            school_name=teacher.school_name
        )
        
        # إحصائيات
        success_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - success_count
        
        logger.info(f"Groups created: {success_count} success, {failed_count} failed")
        
        return Response({
            'success': True,
            'message': f'تم إنشاء {success_count} قروب من أصل {len(sections)}',
            'groups': results,
            'statistics': {
                'total': len(results),
                'success': success_count,
                'failed': failed_count
            }
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating Telegram groups: {e}")
        return Response({
            'error': 'حدث خطأ أثناء إنشاء القروبات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== إنشاء قروبات بـ Client API ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_telegram_groups_client(request):
    """
    إنشاء قروبات تيليجرام باستخدام Client API (Pyrogram)
    يحتاج api_id, api_hash, phone_number
    
    Request Body:
    {
        "grade_name": "الصف الثالث متوسط",
        "subject_name": "المهارات الرقمية",
        "sections": ["أ", "ب", "ج"],
        "phone_number": "+966xxxxxxxxx"  (اختياري - يستخدم من Teacher model إذا لم يُرسل)
    }
    
    Response:
    - إذا كان Session موجود: يبدأ بإنشاء القروبات مباشرة
    - إذا لم يكن Session موجود: يطلب كود التحقق
        {
            "needs_code": true,
            "message": "تم إرسال كود التحقق إلى +966xxx",
            "phone_number": "+966xxx"
        }
    """
    try:
        # الحصول على المعلم
        teacher = get_teacher_from_request(request)
        
        # الحصول على البيانات
        grade_name = request.data.get('grade_name')
        subject_name = request.data.get('subject_name')
        sections = request.data.get('sections', [])
        phone_number = request.data.get('phone_number')
        
        # التحقق من البيانات
        if not grade_name or not subject_name or not sections:
            return Response({
                'error': 'بيانات ناقصة',
                'message': 'يجب توفير اسم الصف، اسم المادة، وقائمة الشُعب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على رقم الهاتف
        if not phone_number:
            # محاولة الحصول من Teacher model
            if hasattr(teacher, 'phone') and teacher.phone:
                phone_number = teacher.phone
            else:
                return Response({
                    'error': 'رقم الهاتف مطلوب',
                    'message': 'يجب توفير رقم الهاتف المُسجل في تيليجرام'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من صيغة رقم الهاتف
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        # التحقق من وجود Session
        from .telegram_session_telethon import telethon_session_manager as session_manager
        
        session_exists = session_manager.is_session_exists(phone_number)
        
        if not session_exists:
            # إرسال كود التحقق
            logger.info(f"No session found for {phone_number}. Sending verification code...")
            
            try:
                result = session_manager.login_and_save_session_sync(phone_number)
                logger.info(f"Session manager result: {result}")
            except Exception as e:
                logger.error(f"Error in login_and_save_session: {e}")
                import traceback
                traceback.print_exc()
                return Response({
                    'error': 'حدث خطأ',
                    'message': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if result['status'] == 'code_required':
                try:
                    # حفظ البيانات مؤقتاً في cache
                    from django.core.cache import cache
                    cache_key = f'pending_groups_{phone_number.replace("+", "")}'
                    
                    logger.info(f"Saving to cache with key: {cache_key}")
                    
                    cache.set(cache_key, {
                        'grade_name': grade_name,
                        'subject_name': subject_name,
                        'sections': sections,
                        'phone_number': phone_number,
                        'phone_code_hash': result['phone_code_hash']
                    }, timeout=600)  # 10 minutes
                    
                    logger.info(f"Code sent successfully. Saved to cache: {cache_key}")
                    
                    return Response({
                        'needs_code': True,
                        'message': f'تم إرسال كود التحقق إلى {phone_number[:8]}***',
                        'phone_number': phone_number,
                        'phone_code_hash': result['phone_code_hash']
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"Error saving to cache: {e}")
                    import traceback
                    traceback.print_exc()
                    return Response({
                        'error': 'خطأ في حفظ البيانات',
                        'message': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                logger.error(f"Unexpected result status: {result['status']}")
                return Response({
                    'error': result.get('message', 'فشل إرسال الكود')
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على credentials من settings
        from django.conf import settings
        api_id = getattr(settings, 'TELEGRAM_API_ID', None)
        api_hash = getattr(settings, 'TELEGRAM_API_HASH', None)
        
        if not api_id or not api_hash:
            return Response({
                'error': 'إعدادات Telegram API غير موجودة',
                'message': 'يجب إضافة TELEGRAM_API_ID و TELEGRAM_API_HASH في settings'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # استيراد الـ Helper
        import subprocess
        import json
        import os
        
        # إنشاء القروبات
        logger.info(f"Creating {len(sections)} Telegram groups with Client API for teacher {teacher.id}")
        
        # المسار للـ script المستقل (Telethon)
        script_path = os.path.join(settings.BASE_DIR, 'create_groups_telethon.py')
        
        # السكريبت يتوقع: phone, grade, subject, school, sections...
        school_name = teacher.school_name if hasattr(teacher, 'school_name') else 'المدرسة'
        
        try:
            # تشغيل الـ script في process منفصل مع UTF-8 encoding
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # تمرير كل section كمعامل منفصل
            script_args = ['python', script_path, phone_number, grade_name, subject_name, school_name] + sections
            
            result = subprocess.run(
                script_args,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
                env=env,
                encoding='utf-8',
                errors='replace'
            )
            
            # طباعة output للـ debugging
            logger.info(f"Script stdout: {result.stdout}")
            logger.error(f"Script stderr: {result.stderr}")
            logger.info(f"Script returncode: {result.returncode}")
            
            # قراءة النتائج من الملف
            output_file = os.path.join(settings.BASE_DIR, 'telegram_groups_results.json')
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                # حذف الملف بعد القراءة
                os.remove(output_file)
            else:
                # إرجاع الخطأ من الـ script
                error_msg = f"لم يتم إنشاء ملف النتائج. Script output:\n{result.stdout}\nErrors:\n{result.stderr}"
                raise Exception(error_msg)
                
        except subprocess.TimeoutExpired:
            raise Exception("انتهت مهلة إنشاء القروبات (5 دقائق)")
        
        # إحصائيات
        success_count = sum(1 for r in results if r.get('success'))
        failed_count = len(results) - success_count
        
        logger.info(f"Groups created: {success_count} success, {failed_count} failed")
        
        return Response({
            'success': True,
            'message': f'تم إنشاء {success_count} قروب من أصل {len(sections)}',
            'results': results,
            'success_count': success_count,
            'total_count': len(results),
            'failed_count': failed_count
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating Telegram groups with Client API: {e}")
        return Response({
            'error': 'حدث خطأ أثناء إنشاء القروبات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_telegram_code(request):
    """
    التحقق من كود Telegram وإكمال إنشاء القروبات
    
    Request Body:
    {
        "code": "12345",
        "phone_number": "+966xxx",
        "phone_code_hash": "xxx"
    }
    """
    try:
        code = request.data.get('code')
        phone_number = request.data.get('phone_number')
        phone_code_hash = request.data.get('phone_code_hash')
        
        if not code or not phone_number or not phone_code_hash:
            return Response({
                'error': 'بيانات ناقصة',
                'message': 'يجب توفير الكود ورقم الهاتف'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من الكود
        from .telegram_session_telethon import telethon_session_manager as session_manager
        
        result = session_manager.verify_code_sync(phone_number, code, phone_code_hash)
        
        if result['status'] != 'success':
            return Response({
                'error': result.get('message', 'فشل التحقق من الكود')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # استرجاع البيانات المؤقتة من cache
        from django.core.cache import cache
        cache_key = f'pending_groups_{phone_number.replace("+", "")}'
        pending_data = cache.get(cache_key)
        
        if not pending_data:
            return Response({
                'error': 'انتهت صلاحية الجلسة',
                'message': 'يرجى البدء من جديد'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # حذف البيانات من cache بعد الاسترجاع
        cache.delete(cache_key)
        
        # الآن جاهزون لإنشاء القروبات
        # نُرجع success وFrontend يعيد استدعاء create API
        return Response({
            'success': True,
            'message': 'تم التحقق بنجاح! جاري إنشاء القروبات...',
            'session_verified': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error verifying Telegram code: {e}")
        return Response({
            'error': 'حدث خطأ أثناء التحقق',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_telegram_permissions(request):
    """
    تطبيق صلاحيات read-only على القروبات المُنشأة مسبقاً
    يقرأ من ملف telegram_groups_results.json
    """
    import subprocess
    import json
    import os
    
    try:
        teacher = request.user
        
        logger.info(f"Applying permissions to Telegram groups for teacher {teacher.id}")
        
        # المسار للـ script
        script_path = os.path.join(settings.BASE_DIR, 'set_group_permissions.py')
        
        # التحقق من وجود ملف النتائج
        output_file = os.path.join(settings.BASE_DIR, 'telegram_groups_results.json')
        if not os.path.exists(output_file):
            return Response({
                'error': 'لم يتم العثور على قروبات مُنشأة مسبقاً',
                'message': 'يجب إنشاء القروبات أولاً'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # تشغيل الـ script
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute timeout
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        
        logger.info(f"Permissions script stdout: {result.stdout}")
        logger.error(f"Permissions script stderr: {result.stderr}")
        
        if result.returncode == 0:
            # نجح - استخراج النتائج من output
            success_count = 0
            total_count = 0
            
            # محاولة قراءة الأرقام من output
            import re
            match = re.search(r'(\d+)/(\d+) succeeded', result.stdout)
            if match:
                success_count = int(match.group(1))
                total_count = int(match.group(2))
            
            return Response({
                'success': True,
                'message': f'تم تطبيق الصلاحيات بنجاح',
                'success_count': success_count,
                'total_count': total_count,
                'output': result.stdout
            }, status=status.HTTP_200_OK)
        else:
            raise Exception(f"Script failed with code {result.returncode}: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        return Response({
            'error': 'انتهت مهلة تطبيق الصلاحيات'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error applying permissions: {e}")
        return Response({
            'error': 'حدث خطأ أثناء تطبيق الصلاحيات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Telegram Session Management ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_session_login(request):
    """بدء عملية ربط حساب تيليجرام - إرسال كود"""
    try:
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response({
                'error': 'رقم الهاتف مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # استخدام FastAPI إذا كان مفعّلاً
        use_fastapi = getattr(settings, 'USE_FASTAPI_TELEGRAM', False)
        
        if use_fastapi:
            try:
                from .telegram_fastapi_client import telegram_fastapi_client
                result = telegram_fastapi_client.send_code(phone_number)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"FastAPI client error: {e}")
                # Fallback to Telethon
                use_fastapi = False
        
        # استخدام Telethon مباشرة
        if not use_fastapi:
            force_sms_raw = request.data.get('force_sms', True)
            if isinstance(force_sms_raw, bool):
                force_sms = force_sms_raw
            else:
                force_sms = str(force_sms_raw).lower() in ('1', 'true', 'yes', 'y', 'on')
            
            try:
                from .telegram_session_telethon import telethon_session_manager as session_manager
            
                # التحقق من وجود session
                if session_manager.is_session_exists(phone_number):
                    return Response({
                        'status': 'already_connected',
                        'message': 'حسابك مربوط مسبقاً!'
                    }, status=status.HTTP_200_OK)
                
                # بدء عملية تسجيل الدخول باستخدام sync wrapper
                result = session_manager.login_and_save_session_sync(phone_number, force_sms=force_sms)
                
                return Response(result, status=status.HTTP_200_OK)
                
            except ImportError as ie:
                logger.error(f"Import error: {ie}")
                return Response({
                    'error': 'Telethon غير مثبت. يرجى تثبيته: pip install telethon',
                    'details': str(ie)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error in session login: {e}", exc_info=True)
        return Response({
            'error': 'حدث خطأ أثناء إرسال الكود',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_session_verify(request):
    """التحقق من كود تيليجرام وإكمال الربط"""
    try:
        from .telegram_session_telethon import telethon_session_manager as session_manager
        
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        phone_code_hash = request.data.get('phone_code_hash')
        
        if not all([phone_number, code, phone_code_hash]):
            return Response({
                'error': 'جميع الحقول مطلوبة'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # استخدام sync wrapper لتجنب مشاكل event loop
        result = session_manager.verify_code_sync(phone_number, code, phone_code_hash)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error verifying code: {e}")
        return Response({
            'error': 'حدث خطأ أثناء التحقق',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_session_password(request):
    """التحقق من كلمة المرور للحسابات المحمية بالتحقق بخطوتين"""
    try:
        from .telegram_session_telethon import telethon_session_manager as session_manager
        
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        if not all([phone_number, password]):
            return Response({
                'error': 'رقم الهاتف وكلمة المرور مطلوبان'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # استخدام sync wrapper لتجنب مشاكل event loop
        result = session_manager.verify_password_sync(phone_number, password)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return Response({
            'error': 'حدث خطأ أثناء التحقق من كلمة المرور',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_session_resend(request):
    """إعادة إرسال كود تيليجرام (قد يحول لطريقة اتصال أخرى)"""
    try:
        from .telegram_session_telethon import telethon_session_manager as session_manager
        
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'رقم الهاتف مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
        
        # استخدام sync wrapper لتجنب مشاكل event loop
        result = session_manager.resend_code_sync(phone_number)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error resending code: {e}")
        return Response({'error': 'فشل إعادة الإرسال', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def telegram_session_status(request):
    """التحقق من حالة ربط تيليجرام"""
    try:
        from .telegram_session_telethon import telethon_session_manager as session_manager
        
        phone_number = request.GET.get('phone_number')
        
        if not phone_number:
            return Response({
                'error': 'رقم الهاتف مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        is_connected = session_manager.is_session_exists(phone_number)
        
        # بدون اختبار Session (لتجنب الأخطاء)
        return Response({
            'is_connected': is_connected,
            'message': 'متصل' if is_connected else 'غير متصل'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error checking session status: {e}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e),
            'is_connected': False,
            'message': 'غير متصل'
        }, status=status.HTTP_200_OK)  # إرجاع 200 بدلاً من 500


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def telegram_session_disconnect(request):
    """فصل ربط حساب تيليجرام"""
    try:
        from .telegram_session_telethon import telethon_session_manager as session_manager
        
        # قراءة phone_number من query params أو body
        phone_number = request.data.get('phone_number') or request.query_params.get('phone_number')
        
        logger.info(f"Disconnect request received for phone: {phone_number}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Query params: {request.query_params}")
        
        if not phone_number:
            logger.warning("Phone number not provided in request")
            return Response({
                'error': 'رقم الهاتف مطلوب',
                'details': 'phone_number field is required in request body or query params'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من وجود session قبل الحذف
        try:
            exists = session_manager.is_session_exists(phone_number)
            logger.info(f"Session exists for {phone_number}: {exists}")
        except Exception as check_error:
            logger.error(f"Error checking session existence: {check_error}")
            # حتى لو فشل الفحص، حاول الحذف
            exists = True
        
        if not exists:
            logger.warning(f"No session found for phone: {phone_number}")
            # نعتبرها نجاح لأن الهدف تحقق (لا يوجد session)
            return Response({
                'success': True,
                'message': 'لا يوجد حساب مربوط بهذا الرقم (تم بالفعل)',
                'phone': phone_number
            }, status=status.HTTP_200_OK)
        
        # محاولة حذف الـ session
        try:
            success = session_manager.delete_session(phone_number)
            logger.info(f"Delete session result for {phone_number}: {success}")
        except Exception as delete_error:
            logger.error(f"Error during session deletion: {delete_error}")
            import traceback
            logger.error(f"Delete traceback: {traceback.format_exc()}")
            return Response({
                'error': 'حدث خطأ أثناء حذف الملف',
                'details': str(delete_error)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if success:
            logger.info(f"Session deleted successfully for: {phone_number}")
            return Response({
                'success': True,
                'message': 'تم فصل الحساب بنجاح',
                'phone': phone_number
            }, status=status.HTTP_200_OK)
        else:
            # الملف غير موجود أو تم حذفه بالفعل
            logger.warning(f"Session file not found for: {phone_number}")
            return Response({
                'success': True,
                'message': 'تم فصل الحساب (الملف غير موجود)',
                'phone': phone_number
            }, status=status.HTTP_200_OK)
        
    except ImportError as ie:
        logger.error(f"Import error in disconnect: {ie}")
        return Response({
            'error': 'خطأ في تحميل مكتبات تيليجرام',
            'details': str(ie)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error disconnecting session: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': 'حدث خطأ أثناء فصل الحساب',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_session_reset(request):
    """إعادة تعيين session (حذف session غير صالح)"""
    try:
        from .telegram_session_telethon import telethon_session_manager as session_manager
        
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response({
                'error': 'رقم الهاتف مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # حذف الـ session بالقوة
        success = session_manager.delete_session(phone_number)
        
        return Response({
            'success': True,
            'message': 'تم إعادة تعيين Session. يمكنك المحاولة مرة أخرى.',
            'session_deleted': success
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error resetting session: {e}")
        return Response({
            'error': 'حدث خطأ أثناء إعادة التعيين',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Telegram Groups Creation ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_telegram_groups_for_grade(request, grade_id):
    """
    إنشاء قروبات تيليجرام لجميع شُعب صف معين
    
    POST /api/sections/grade/<id>/create-telegram-groups/
    Body: {
        "phone_number": "+966558048004"
    }
    """
    try:
        # التحقق من وجود الصف وأنه يخص المعلم
        grade = get_object_or_404(SchoolGrade, id=grade_id, teacher=request.user.teacher)
        
        # التحقق من البيانات
        serializer = CreateTelegramGroupsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data['phone_number']
        
        # جلب جميع الشُعب
        sections = grade.sections.filter(is_active=True)
        
        if not sections.exists():
            return Response({
                'success': False,
                'message': 'لا توجد شُعب لهذا الصف'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # استيراد create_groups_standalone
        import subprocess
        import sys
        import os
        from django.conf import settings
        
        results = []
        success_count = 0
        total_count = sections.count()
        
        # إنشاء قروبات لكل شُعبة
        for section in sections:
            try:
                # التحقق من وجود قروب سابق
                if hasattr(section, 'telegram_group'):
                    results.append({
                        'section_id': section.id,
                        'section_name': section.section_name,
                        'success': False,
                        'message': 'قروب موجود مسبقاً',
                        'invite_link': section.telegram_group.invite_link
                    })
                    continue
                
                # بناء اسم القروب
                level_display = dict(grade.LEVEL_CHOICES)[grade.level]
                group_name = f"{level_display} {grade.grade_number} {section.section_name} - {grade.school_name}"
                
                # الحصول على اسم المعلم الكامل
                teacher_full_name = grade.teacher.get_full_name()
                
                # استخدام سكريبت standalone لإنشاء قروب واحد
                script_path = os.path.join(settings.BASE_DIR, 'create_groups_standalone.py')
                
                # تنفيذ السكريبت
                result = subprocess.run(
                    [
                        sys.executable,
                        script_path,
                        f"{level_display} {grade.grade_number}",
                        grade.school_name,
                        section.section_name,
                        phone_number,
                        teacher_full_name  # إضافة اسم المعلم
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 دقيقة timeout
                    cwd=settings.BASE_DIR
                )
                
                # تحليل النتيجة
                if result.returncode == 0:
                    # محاولة استخراج chat_id و invite_link من output
                    output_lines = result.stdout.strip().split('\n')
                    chat_id = None
                    invite_link = None
                    
                    for line in output_lines:
                        if 'chat_id:' in line.lower():
                            try:
                                chat_id = int(line.split(':')[1].strip())
                            except:
                                pass
                        elif 'https://t.me/' in line:
                            invite_link = line.strip()
                    
                    # ✅ تحويل chat_id إلى سالب تلقائياً
                    normalized_chat_id = normalize_telegram_chatid(chat_id)
                    logger.info(f"Script chat_id: {chat_id}, Normalized: {normalized_chat_id}")
                    
                    # حفظ في Database
                    telegram_group = TelegramGroup.objects.create(
                        section=section,
                        group_name=group_name,
                        chat_id=normalized_chat_id,  # ✅ حفظ سالب
                        invite_link=invite_link,
                        created_by_phone=phone_number,
                        is_bot_added=True,  # السكريبت يضيف البوت
                        instructions_sent=True,  # السكريبت يرسل التعليمات
                        permissions_applied=True,  # السكريبت يطبق الصلاحيات
                        status='bot_added',
                        creation_metadata={
                            'script_output': result.stdout,
                            'created_at': timezone.now().isoformat()
                        }
                    )
                    
                    success_count += 1
                    results.append({
                        'section_id': section.id,
                        'section_name': section.section_name,
                        'group_name': group_name,
                        'chat_id': chat_id,
                        'invite_link': invite_link,
                        'success': True,
                        'telegram_group_id': telegram_group.id
                    })
                else:
                    # فشل الإنشاء
                    error_msg = result.stderr or result.stdout or 'خطأ غير معروف'
                    
                    # حفظ في Database مع حالة خطأ
                    TelegramGroup.objects.create(
                        section=section,
                        group_name=group_name,
                        created_by_phone=phone_number,
                        status='error',
                        error_message=error_msg[:500],
                        creation_metadata={
                            'script_output': result.stdout,
                            'script_error': result.stderr,
                            'return_code': result.returncode
                        }
                    )
                    
                    results.append({
                        'section_id': section.id,
                        'section_name': section.section_name,
                        'group_name': group_name,
                        'success': False,
                        'error': error_msg[:200]
                    })
                
            except subprocess.TimeoutExpired:
                results.append({
                    'section_id': section.id,
                    'section_name': section.section_name,
                    'success': False,
                    'error': 'انتهت مهلة الإنشاء (timeout)'
                })
            except Exception as section_error:
                logger.error(f"Error creating group for section {section.id}: {section_error}")
                results.append({
                    'section_id': section.id,
                    'section_name': section.section_name,
                    'success': False,
                    'error': str(section_error)
                })
        
        # النتيجة النهائية
        return Response({
            'success': success_count > 0,
            'message': f'تم إنشاء {success_count} من {total_count} قروبات',
            'success_count': success_count,
            'total_count': total_count,
            'results': results,
            'grade_info': {
                'id': grade.id,
                'display_name': grade.display_name,
                'school_name': grade.school_name
            }
        }, status=status.HTTP_200_OK if success_count > 0 else status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error in create_telegram_groups: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'حدث خطأ أثناء إنشاء القروبات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_single_telegram_group(request):
    """
    إنشاء قروب تيليجرام واحد فقط (للمعالجة المتسلسلة)
    
    Request Body:
    {
        "grade_name": "الصف الثالث متوسط",
        "subject_name": "المهارات الرقمية",
        "section": "أ",
        "phone_number": "+966xxxxxxxxx"
    }
    
    Response:
    {
        "success": true,
        "group": {
            "group_name": "...",
            "invite_link": "...",
            "chat_id": "...",
            "steps_completed": ["create", "welcome", "convert", ...]
        }
    }
    """
    import time
    start_time = time.time()
    
    try:
        # الحصول على المعلم
        teacher = get_teacher_from_request(request)
        
        # الحصول على البيانات
        grade_name = request.data.get('grade_name')
        subject_name = request.data.get('subject_name')
        section = request.data.get('section')  # حرف واحد فقط
        phone_number = request.data.get('phone_number')
        school_name = request.data.get('school_name')  # اسم المدرسة من الـ frontend
        
        # التحقق من البيانات
        if not grade_name or not subject_name or not section:
            return Response({
                'success': False,
                'error': 'بيانات ناقصة',
                'message': 'يجب توفير اسم الصف، اسم المادة، والشعبة'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على رقم الهاتف
        if not phone_number:
            if hasattr(teacher, 'phone') and teacher.phone:
                phone_number = teacher.phone
            else:
                return Response({
                    'success': False,
                    'error': 'رقم الهاتف مطلوب'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من صيغة رقم الهاتف
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        # الحصول على credentials من settings
        from django.conf import settings
        api_id = getattr(settings, 'TELEGRAM_API_ID', None)
        api_hash = getattr(settings, 'TELEGRAM_API_HASH', None)
        
        if not api_id or not api_hash:
            return Response({
                'success': False,
                'error': 'إعدادات Telegram API غير موجودة'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # إنشاء قروب واحد
        logger.info(f"Creating single Telegram group: {grade_name} {section} - {subject_name}")
        
        import subprocess
        import json
        import os
        
        # المسار للـ script المستقل (Telethon)
        script_path = os.path.join(settings.BASE_DIR, 'create_groups_telethon.py')
        
        try:
            # تشغيل الـ script لقروب واحد فقط
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # السكريبت يتوقع: phone, grade, subject, school, teacher_name, sections...
            # إذا لم يتم إرسال school_name من الـ frontend، استخدم من بيانات المعلم
            if not school_name:
                school_name = getattr(teacher, 'school_name', 'المدرسة')
            teacher_name = teacher.full_name if teacher.full_name else teacher.email.split('@')[0]
            
            result = subprocess.run(
                [
                    'python', script_path,
                    phone_number, grade_name, subject_name, school_name, teacher_name, section
                ],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutes timeout للقروب الواحد
                env=env,
                encoding='utf-8',
                errors='replace'
            )
            
            logger.info(f"Script stdout: {result.stdout}")
            if result.stderr:
                logger.error(f"Script stderr: {result.stderr}")
            
            # قراءة النتائج
            output_file = os.path.join(settings.BASE_DIR, 'telegram_groups_results.json')
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    results_data = json.load(f)
                
                # حذف الملف بعد القراءة
                os.remove(output_file)
                
                if results_data and len(results_data) > 0:
                    group_result = results_data[0]  # أول (وفقط) قروب
                    
                    # ✅ Log البيانات المستلمة
                    logger.info(f"📦 Group result received:")
                    logger.info(f"   success: {group_result.get('success')}")
                    logger.info(f"   group_name: {group_result.get('group_name')}")
                    logger.info(f"   invite_link: {group_result.get('invite_link', '(NOT FOUND)')}")
                    logger.info(f"   chat_id: {group_result.get('chat_id', '(NOT FOUND)')}")
                    
                    elapsed_time = time.time() - start_time
                    
                    if group_result.get('success'):
                        # 🆕 حفظ البيانات في telegram_groups
                        try:
                            # البحث عن الشعبة المناسبة
                            from apps.sections.models import SchoolGrade, Section, TelegramGroup
                            
                            # البحث عن الصف بناءً على المعلم واسم الصف
                            # نستخرج رقم الصف من grade_name (مثل: "الصف الثالث متوسط" -> 3)
                            grade_parts = grade_name.split()
                            grade_numbers = {
                                'الأول': 1, 'الاول': 1, 'اول': 1,
                                'الثاني': 2, 'ثاني': 2,
                                'الثالث': 3, 'ثالث': 3,
                                'الرابع': 4, 'رابع': 4,
                                'الخامس': 5, 'خامس': 5,
                                'السادس': 6, 'سادس': 6,
                                'السابع': 7, 'سابع': 7,
                                'الثامن': 8, 'ثامن': 8,
                                'التاسع': 9, 'تاسع': 9,
                                'العاشر': 10, 'عاشر': 10,
                                'الحادي عشر': 11, 'حادي عشر': 11,
                                'الثاني عشر': 12, 'ثاني عشر': 12
                            }
                            
                            grade_number = None
                            for part in grade_parts:
                                if part in grade_numbers:
                                    grade_number = grade_numbers[part]
                                    break
                            
                            if not grade_number:
                                logger.warning(f"Could not extract grade number from: {grade_name}")
                                # محاولة البحث بدون رقم الصف
                                school_grade = SchoolGrade.objects.filter(
                                    teacher=teacher,
                                    school_name=school_name
                                ).first()
                            else:
                                # البحث عن الصف
                                school_grade = SchoolGrade.objects.filter(
                                    teacher=teacher,
                                    grade_number=grade_number,
                                    school_name=school_name
                                ).first()
                            
                            if school_grade:
                                # البحث عن الشعبة
                                section_obj = Section.objects.filter(
                                    grade=school_grade,
                                    section_name=section
                                ).first()
                                
                                if section_obj:
                                    # ✅ تحويل chat_id إلى سالب تلقائياً
                                    raw_chat_id = group_result.get('chat_id')
                                    normalized_chat_id = normalize_telegram_chatid(raw_chat_id)
                                    
                                    # التحقق من عدم وجود سجل سابق
                                    telegram_group, created = TelegramGroup.objects.get_or_create(
                                        section=section_obj,
                                        defaults={
                                            'group_name': group_result['group_name'],
                                            'chat_id': normalized_chat_id,  # ✅ حفظ سالب
                                            'invite_link': group_result['invite_link'],
                                            'created_by_phone': phone_number,
                                            'status': 'created',
                                            'bot_username': 'SmartEduProjectBot',
                                            'is_bot_added': True,
                                            'is_bot_admin': False,
                                            'read_only_mode': True,
                                            'permissions_applied': False,
                                            'instructions_sent': False,
                                            'instructions_pinned': False,
                                            'creation_metadata': {
                                                'created_from': 'sections-setup',
                                                'grade_name': grade_name,
                                                'subject_name': subject_name,
                                                'elapsed_time': elapsed_time
                                            }
                                        }
                                    )
                                    
                                    if not created:
                                        # تحديث السجل الموجود
                                        telegram_group.group_name = group_result['group_name']
                                        telegram_group.chat_id = normalized_chat_id  # ✅ تحديث سالب
                                        telegram_group.invite_link = group_result['invite_link']
                                        telegram_group.created_by_phone = phone_number
                                        telegram_group.status = 'created'
                                        telegram_group.is_bot_added = True
                                        telegram_group.save()
                                        logger.info(f"Updated existing TelegramGroup for section {section_obj.id}")
                                    else:
                                        logger.info(f"Created new TelegramGroup for section {section_obj.id}")
                                else:
                                    logger.warning(f"Section '{section}' not found in grade {school_grade.id}")
                            else:
                                logger.warning(f"SchoolGrade not found for teacher {teacher.id}, grade_number {grade_number}")
                                
                        except Exception as save_error:
                            logger.error(f"Error saving to TelegramGroup: {str(save_error)}")
                            # نستمر بدون فشل الـ API
                        
                        # إرجاع البيانات في root level و group object للتوافق
                        response_data = {
                            'success': True,
                            # ✅ البيانات في الـ root للتوافق مع Frontend
                            'section': section,
                            'invite_link': group_result['invite_link'],
                            'link': group_result['invite_link'],  # alias
                            'telegram_link': group_result['invite_link'],  # alias
                            'chat_id': group_result.get('chat_id'),
                            'group_id': group_result.get('chat_id'),  # alias
                            # البيانات الكاملة في group object
                            'group': {
                                'group_name': group_result['group_name'],
                                'section': section,
                                'invite_link': group_result['invite_link'],
                                'chat_id': group_result.get('chat_id'),
                                'steps_completed': [
                                    'create', 'welcome', 'convert', 
                                    'history', 'pin', 'readonly', 
                                    'bot', 'promote'
                                ],
                                'elapsed_time': round(elapsed_time, 2)
                            },
                            'message': f'تم إنشاء القروب بنجاح في {elapsed_time:.1f} ثانية'
                        }
                        
                        logger.info(f"✅ Returning response with invite_link: {group_result['invite_link'][:50]}...")
                        
                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        error_msg = group_result.get('error', 'فشل في الإنشاء')
                        logger.error(f"Group creation failed: {error_msg}")
                        logger.error(f"Script output: {result.stdout}")
                        
                        return Response({
                            'success': False,
                            'error': error_msg,
                            'group_name': group_result.get('group_name'),
                            'section': section,
                            'script_output': result.stdout[-500:] if result.stdout else ''  # آخر 500 حرف
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        'success': False,
                        'error': 'لم يتم إرجاع نتائج من السكربت'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'success': False,
                    'error': 'ملف النتائج غير موجود'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except subprocess.TimeoutExpired:
            return Response({
                'success': False,
                'error': 'انتهت مهلة الإنشاء',
                'message': 'استغرق إنشاء القروب وقتاً طويلاً'
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
            
        except Exception as e:
            logger.error(f"Error in subprocess: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': 'خطأ في تشغيل السكربت',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in create_single_telegram_group: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'حدث خطأ أثناء إنشاء القروب',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_group_permissions(request):
    """
    تفعيل صلاحيات القروب الكاملة:
    1. تطبيق صلاحيات القراءة فقط للأعضاء
    2. إظهار سجل المحادثة للأعضاء الجدد
    3. ترقية البوت بصلاحيات كاملة
    
    Request Body:
    {
        "chat_id": "-1001234567890",
        "phone_number": "+966xxxxxxxxx"
    }
    
    Response:
    {
        "success": true,
        "message": "تم تفعيل الصلاحيات بنجاح",
        "permissions": {
            "members_readonly": true,
            "history_visible": true,
            "bot_promoted": true
        }
    }
    """
    try:
        # الحصول على المعلم
        teacher = get_teacher_from_request(request)
        
        # الحصول على البيانات
        chat_id = request.data.get('chat_id')
        phone_number = request.data.get('phone_number')
        
        # التحقق من البيانات
        if not chat_id:
            return Response({
                'success': False,
                'error': 'chat_id مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على رقم الهاتف
        if not phone_number:
            if hasattr(teacher, 'phone') and teacher.phone:
                phone_number = teacher.phone
            else:
                return Response({
                    'success': False,
                    'error': 'رقم الهاتف مطلوب'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من صيغة رقم الهاتف
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        logger.info(f"Activating permissions for chat {chat_id} using phone {phone_number}")
        
        # استيراد المكتبات
        import subprocess
        import json
        import os
        from django.conf import settings
        
        # استخدام سكربت Telethon المستقل
        script_path = os.path.join(settings.BASE_DIR, 'activate_permissions_telethon.py')
        bot_username = settings.TELEGRAM_BOT_USERNAME or 'SmartEduProjectBot'
        
        try:
            # تشغيل السكربت
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            logger.info(f"Running Telethon script: {script_path}")
            logger.info(f"Parameters: chat_id={chat_id}, phone={phone_number}, bot={bot_username}")
            
            result = subprocess.run(
                ['python', script_path, str(chat_id), phone_number, bot_username],
                capture_output=True,
                text=True,
                timeout=180,  # 3 minutes timeout (enough for Telegram operations)
                env=env,
                encoding='utf-8',
                errors='replace'
            )
            
            logger.info(f"Activate permissions stdout: {result.stdout}")
            if result.stderr:
                logger.error(f"Activate permissions stderr: {result.stderr}")
            
            # استخراج النتيجة من output
            import re
            json_match = re.search(r'RESULT_JSON: (.+)', result.stdout)
            if json_match:
                result_data = json.loads(json_match.group(1))
                
                if result_data.get('success'):
                    return Response(result_data, status=status.HTTP_200_OK)
                else:
                    return Response(result_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'success': False,
                    'error': 'لم يتم العثور على نتيجة',
                    'output': result.stdout
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except subprocess.TimeoutExpired:
            return Response({
                'success': False,
                'error': 'انتهت مهلة التفعيل'
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
            
        except Exception as e:
            logger.error(f"Error in subprocess: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': 'خطأ في التفعيل',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in activate_group_permissions: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'حدث خطأ أثناء تفعيل الصلاحيات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Student Registration & Join Links ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_students_count(request):
    """
    الحصول على العدد الفعلي للطلاب المسجلين للمعلم
    """
    try:
        teacher = get_teacher_from_request(request)
        
        from .models import StudentRegistration
        total_count = StudentRegistration.objects.filter(teacher=teacher).count()
        
        return Response({
            'success': True,
            'total': total_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_students_count: {str(e)}")
        return Response({
            'error': 'حدث خطأ في جلب العدد',
            'total': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_teacher_join_link(request):
    """
    توليد رابط انضمام تلقائي للمعلم
    
    Request Body (اختياري):
    {
        "password": "مدرستي2025"  // اختياري - لحماية الرابط
    }
    
    Response:
    {
        "success": true,
        "join_url": "/join/basem902",
        "full_url": "http://localhost:8000/join/basem902",
        "has_password": true,
        "created": false,
        "stats": {
            "views": 156,
            "registrations": 42
        }
    }
    """
    try:
        teacher = get_teacher_from_request(request)
        
        # 🔐 الحصول على كلمة المرور من request (اختياري)
        password = request.data.get('password', None)
        if password:
            password = password.strip()
            if not password:
                password = None
        
        # ✅ توليد token من email أو phone أو user.username
        token = None
        
        # محاولة 1: استخدام user.username (إذا كان موجوداً)
        if teacher.user and hasattr(teacher.user, 'username'):
            token = teacher.user.username
        
        # محاولة 2: استخدام email (الجزء قبل @)
        if not token and teacher.email:
            token = teacher.email.split('@')[0]
            # تنظيف token من الأحرف غير المسموحة
            import re
            token = re.sub(r'[^a-zA-Z0-9_]', '', token)
        
        # محاولة 3: استخدام phone
        if not token and teacher.phone:
            token = f"teacher_{teacher.phone}"
        
        # محاولة 4: استخدام ID كـ fallback
        if not token:
            token = f"teacher_{teacher.id}"
        
        logger.info(f"Generated token for teacher {teacher.id}: {token}, has_password: {bool(password)}")
        
        # إنشاء أو الحصول على الرابط
        from .models import TeacherJoinLink
        link, created = TeacherJoinLink.objects.get_or_create(
            teacher=teacher,
            defaults={
                'join_token': token,
                'join_url': f'/join/{token}',
                'password': password,
                'is_active': True
            }
        )
        
        # إذا كان الرابط موجود مسبقاً، نحدث البيانات
        if not created:
            update_fields = []
            
            if link.join_token != token:
                link.join_token = token
                link.join_url = f'/join/{token}'
                update_fields.extend(['join_token', 'join_url'])
                logger.info(f"Updated token for existing link to: {token}")
            
            # 🔐 تحديث كلمة المرور (حتى لو كانت None)
            if link.password != password:
                link.password = password
                update_fields.append('password')
                logger.info(f"Updated password for link (has_password: {bool(password)})")
            
            if update_fields:
                link.save(update_fields=update_fields)
        
        # بناء الرابط الكامل (استخدام Frontend URL من settings)
        from django.conf import settings
        actual_token = link.join_token
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
        # ✅ استخدام الرابط الكامل المباشر (Live Server لا يدعم URL rewriting)
        full_url = f'{frontend_url}/pages/join.html?token={actual_token}'
        
        logger.info(f"Teacher {teacher.id} {'created' if created else 'accessed'} join link: {full_url}")
        
        return Response({
            'success': True,
            'join_url': f'/join/{actual_token}',
            'full_url': full_url,
            'token': actual_token,
            'has_password': bool(link.password),  # 🔐
            'created': created,
            'stats': {
                'views': link.views_count,
                'registrations': link.registrations_count
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in generate_teacher_join_link: {str(e)}")
        return Response({
            'error': 'حدث خطأ في توليد الرابط',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # ✅ Public API - لا يحتاج تسجيل دخول
def get_teacher_join_info(request, token):
    """
    جلب معلومات المعلم من الرابط (Public - بدون تسجيل دخول)
    
    URL: /api/sections/join/basem902/info/
    
    GET: فحص وجود الرابط وهل له كلمة مرور
    POST: التحقق من كلمة المرور (إذا موجودة)
    
    POST Body:
    {
        "password": "مدرستي2025"
    }
    
    Response:
    {
        "success": true,
        "has_password": true,
        "password_required": true,  // يحتاج كلمة مرور
        "teacher": {
            "name": "باسم محمد",
            "school": "الثانوية الأولى",
            "subject": "المهارات الرقمية"
        },
        "grades": [...],
        "welcome_message": "مرحباً بك..."
    }
    """
    try:
        from .models import TeacherJoinLink
        
        # البحث عن رابط المعلم
        teacher_link = TeacherJoinLink.objects.select_related('teacher').get(
            join_token=token,
            is_active=True
        )
        
        # 🔐 التحقق من كلمة المرور (إذا موجودة)
        if teacher_link.password:
            # إذا كان GET request، نرجع فقط has_password=true
            if request.method == 'GET':
                return Response({
                    'success': False,
                    'has_password': True,
                    'password_required': True,
                    'message': 'هذا الرابط محمي بكلمة مرور'
                }, status=status.HTTP_200_OK)
            
            # إذا كان POST request، نتحقق من كلمة المرور
            provided_password = request.data.get('password', '')
            if provided_password.strip() != teacher_link.password:
                return Response({
                    'success': False,
                    'has_password': True,
                    'password_required': True,
                    'error': 'كلمة المرور غير صحيحة'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # ✅ كلمة المرور صحيحة، نكمل
            logger.info(f"Password verified for token: {token}")
        
        # تحديث عدد المشاهدات
        teacher_link.views_count += 1
        teacher_link.save(update_fields=['views_count'])
        
        teacher = teacher_link.teacher
        
        # جلب الصفوف والشُعب
        grades = SchoolGrade.objects.filter(
            teacher=teacher,
            is_active=True
        ).prefetch_related('sections')
        
        grades_data = []
        for grade in grades:
            sections_data = []
            for section in grade.sections.all():
                sections_data.append({
                    'id': section.id,
                    'name': section.section_name,
                    'has_telegram': hasattr(section, 'telegram_group')
                })
            
            grades_data.append({
                'id': grade.id,
                'name': grade.display_name,  # ✅ استخدام display_name بدلاً من get_full_name()
                'sections': sections_data
            })
        
        logger.info(f"Join link info accessed for teacher {teacher.id}, token: {token}")
        
        # ✅ اسم المعلم
        teacher_name = teacher.full_name
        if not teacher_name and teacher.user:
            teacher_name = getattr(teacher.user, 'username', 'المعلم')
        if not teacher_name:
            teacher_name = 'المعلم'
        
        return Response({
            'success': True,
            'has_password': bool(teacher_link.password),  # 🔐
            'password_required': False,  # كلمة المرور تم التحقق منها
            'teacher': {
                'name': teacher_name,
                'school': teacher.school_name or 'مدرستي',
                'subject': getattr(teacher, 'subject_name', 'المادة الدراسية')
            },
            'grades': grades_data,
            'welcome_message': 'مرحباً بك عزيزي الطالب\n\nأهلاً بك في منصة SmartEdu التعليمية\n\nيسعدنا انضمامك إلى القروب التعليمي الخاص بك على Telegram'
        }, status=status.HTTP_200_OK)
        
    except TeacherJoinLink.DoesNotExist:
        return Response({
            'error': 'رابط غير صالح أو منتهي الصلاحية'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_teacher_join_info: {str(e)}")
        return Response({
            'error': 'حدث خطأ في جلب المعلومات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ Public API - لا يحتاج تسجيل دخول
def register_student(request, token):
    """
    تسجيل طالب من خلال رابط المعلم (Public - بدون تسجيل دخول)
    
    Request:
    {
        "full_name": "محمد أحمد علي حسن",
        "grade_id": 123,
        "section_id": 456
    }
    
    Response (Success):
    {
        "success": true,
        "student": {
            "name": "محمد أحمد علي حسن",
            "grade": "الثالث متوسط",
            "section": "أ"
        },
        "telegram": {
            "group_name": "المهارات الرقمية - الثالث متوسط - أ",
            "invite_link": "https://t.me/+xyz"
        }
    }
    
    Response (Duplicate):
    {
        "success": false,
        "duplicate": true,
        "similar_name": "محمد أحمد علي",
        "similarity": 85.5,
        "message": "يوجد طالب مسجل باسم مشابه..."
    }
    """
    try:
        from .models import TeacherJoinLink, StudentRegistration, TelegramGroup
        from .serializers import StudentRegistrationSerializer
        from .utils import (
            ArabicNameNormalizer, 
            StudentDuplicateChecker,
            IPAddressHelper
        )
        
        # التحقق من الرابط
        teacher_link = TeacherJoinLink.objects.select_related('teacher').get(
            join_token=token,
            is_active=True
        )
        
        teacher = teacher_link.teacher
        
        # Validation
        serializer = StudentRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        full_name = data['full_name'].strip()
        grade_id = data['grade_id']
        section_id = data['section_id']
        
        # التحقق من الصف والشعبة
        logger.info(f"Looking for section: grade_id={grade_id}, section_id={section_id}, teacher_id={teacher.id}")
        
        section = Section.objects.select_related('grade').get(
            id=section_id,
            grade_id=grade_id,
            grade__teacher=teacher,
            grade__is_active=True
        )
        
        logger.info(f"✅ Found section: {section.id} - {section.section_name} in grade {section.grade.display_name}")
        
        # تطبيع الاسم
        normalized_name = ArabicNameNormalizer.normalize(full_name)
        
        # التحقق من التكرار
        duplicate_check = StudentDuplicateChecker.check_duplicate(
            teacher.id,
            grade_id,
            section_id,
            full_name
        )
        
        if duplicate_check['is_duplicate']:
            return Response({
                'success': False,
                'duplicate': True,
                'similar_name': duplicate_check['similar_name'],
                'similarity': duplicate_check['similarity'],
                'message': duplicate_check['message']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # البحث عن رابط التليجرام
        from .models import SectionLink
        
        telegram_group = None
        telegram_link = None
        group_name = None
        
        logger.info(f"Looking for Telegram link for section_id: {section.id}")
        
        try:
            # ✅ محاولة 1: البحث في SectionLink
            section_link = SectionLink.objects.get(section=section)
            telegram_link = section_link.telegram_link
            group_name = f"{section.grade.display_name} - {section.section_name}"
            logger.info(f"✅ Found SectionLink with telegram_link: {telegram_link}")
        except SectionLink.DoesNotExist:
            logger.warning(f"❌ No SectionLink found for section_id: {section.id}")
            
            # ✅ محاولة 2: البحث في TelegramGroup (للتوافق مع النظام القديم)
            try:
                telegram_group = TelegramGroup.objects.get(section=section)
                telegram_link = telegram_group.invite_link
                group_name = telegram_group.group_name
                logger.info(f"✅ Found TelegramGroup: {group_name}, link: {telegram_link}")
            except TelegramGroup.DoesNotExist:
                logger.warning(f"❌ No TelegramGroup found either for section_id: {section.id}")
                pass
        
        # حفظ الطالب
        student = StudentRegistration.objects.create(
            full_name=full_name,
            normalized_name=normalized_name,
            teacher=teacher,
            school_name=teacher.school_name or 'مدرستي',
            grade=section.grade,
            section=section,
            telegram_group=telegram_group,
            telegram_invite_link=telegram_link or '',  # ✅ استخدام string فارغ بدلاً من None
            registration_ip=IPAddressHelper.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        # تحديث الإحصائيات
        teacher_link.registrations_count += 1
        teacher_link.save(update_fields=['registrations_count'])
        
        # ✅ تحديث عدد الطلاب في الشعبة
        section.update_student_count()
        
        logger.info(f"Student registered: {full_name} in section {section.id} via token {token}")
        
        response_data = {
            'success': True,
            'message': 'تم التسجيل بنجاح',
            'student': {
                'name': student.full_name,
                'grade': section.grade.display_name,  # ✅ استخدام display_name بدلاً من get_full_name()
                'section': section.section_name
            }
        }
        
        # إضافة معلومات التليجرام إذا وجدت
        if telegram_link:
            response_data['telegram'] = {
                'group_name': group_name,
                'invite_link': telegram_link
            }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except TeacherJoinLink.DoesNotExist:
        return Response({
            'error': 'رابط غير صالح أو منتهي الصلاحية'
        }, status=status.HTTP_404_NOT_FOUND)
    except Section.DoesNotExist:
        return Response({
            'error': 'الشعبة غير موجودة أو غير نشطة'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in register_student: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        
        from django.conf import settings
        response_data = {
            'error': 'حدث خطأ في التسجيل',
            'details': str(e)
        }
        
        # إضافة traceback فقط في DEBUG mode
        if settings.DEBUG:
            response_data['traceback'] = error_traceback
        
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== إدارة مواد المعلمين ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_subjects_to_sections(request):
    """
    تعيين المواد للشُعب
    
    Body:
    {
        "grade_id": 1,
        "section_ids": [1, 2, 3],
        "subject_names": ["المهارات الرقمية", "العلوم"]
    }
    """
    try:
        # Get teacher
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'المعلم غير موجود'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validate data
        serializer = AssignSubjectsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        grade = data['grade']
        sections = data['sections']
        subject_names = data['subject_names']
        
        # Check grade belongs to teacher
        if grade.teacher != teacher:
            return Response({
                'error': 'هذا الصف لا ينتمي لك'
            }, status=status.HTTP_403_FORBIDDEN)
        
        created_count = 0
        updated_count = 0
        results = []
        
        with transaction.atomic():
            for section in sections:
                for subject_name in subject_names:
                    # Check if exists
                    teacher_subject, created = TeacherSubject.objects.get_or_create(
                        teacher=teacher,
                        grade=grade,
                        section=section,
                        subject_name=subject_name,
                        defaults={
                            'teacher_phone': teacher.phone,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        created_count += 1
                        results.append({
                            'section': section.section_name,
                            'subject': subject_name,
                            'status': 'created'
                        })
                    else:
                        # Update if inactive
                        if not teacher_subject.is_active:
                            teacher_subject.is_active = True
                            teacher_subject.save()
                            updated_count += 1
                            results.append({
                                'section': section.section_name,
                                'subject': subject_name,
                                'status': 'reactivated'
                            })
                        else:
                            results.append({
                                'section': section.section_name,
                                'subject': subject_name,
                                'status': 'already_exists'
                            })
        
        return Response({
            'success': True,
            'message': f'تم تعيين المواد بنجاح',
            'created': created_count,
            'updated': updated_count,
            'results': results,
            'total': len(results)
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in assign_subjects_to_sections: {str(e)}")
        return Response({
            'error': 'حدث خطأ في تعيين المواد',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_section_subjects(request, section_id):
    """
    الحصول على المواد المعينة لشعبة معينة
    """
    try:
        # Get teacher
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'المعلم غير موجود'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get section
        section = Section.objects.filter(
            id=section_id,
            grade__teacher=teacher,
            is_active=True
        ).first()
        
        if not section:
            return Response({
                'error': 'الشعبة غير موجودة'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get subjects
        subjects = TeacherSubject.objects.filter(
            section=section,
            teacher=teacher,
            is_active=True
        )
        
        serializer = TeacherSubjectSerializer(subjects, many=True)
        
        return Response({
            'success': True,
            'section': {
                'id': section.id,
                'name': section.section_name,
                'grade': section.grade.display_name
            },
            'subjects': serializer.data,
            'count': subjects.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_section_subjects: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fix_telegram_chatid(request):
    """
    Fix Telegram Group chat_id from positive to negative
    تصحيح chat_id من موجب إلى سالب (-100 prefix)
    """
    try:
        # Get teacher
        teacher = Teacher.objects.get(user=request.user)
        
        # Get all telegram groups with positive chat_id
        groups_to_fix = TelegramGroup.objects.filter(
            section__grade__teacher=teacher,
            chat_id__gt=0
        )
        
        total_count = groups_to_fix.count()
        
        if total_count == 0:
            return Response({
                'success': True,
                'message': 'جميع المجموعات صحيحة بالفعل',
                'fixed_count': 0
            }, status=status.HTTP_200_OK)
        
        fixed_count = 0
        fixed_groups = []
        
        for group in groups_to_fix:
            old_chat_id = group.chat_id
            # Convert: 3298260616 → -1003298260616
            new_chat_id = int(f'-100{old_chat_id}')
            
            group.chat_id = new_chat_id
            group.save(update_fields=['chat_id'])
            
            fixed_groups.append({
                'id': group.id,
                'section_id': group.section_id,
                'group_name': group.group_name,
                'old_chat_id': old_chat_id,
                'new_chat_id': new_chat_id
            })
            fixed_count += 1
        
        logger.info(f"Fixed {fixed_count} Telegram groups for teacher {teacher.full_name}")
        
        return Response({
            'success': True,
            'message': f'تم تصحيح {fixed_count} مجموعة بنجاح',
            'fixed_count': fixed_count,
            'groups': fixed_groups
        }, status=status.HTTP_200_OK)
        
    except Teacher.DoesNotExist:
        return Response({
            'error': 'المعلم غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in fix_telegram_chatid: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== التحقق من الطالب للانضمام ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_student_for_join(request):
    """
    التحقق من الطالب قبل الانضمام إلى قروب التليجرام
    
    Request Body:
    {
        "student_name": "باسم محمد علي أحمد",
        "section_id": 6
    }
    
    Response:
    {
        "success": true,
        "student": {
            "name": "...",
            "grade": "...",
            "section": "...",
            "school": "..."
        },
        "telegram_group": {
            "name": "...",
            "invite_link": "...",
            "chat_id": -1001234567890
        }
    }
    """
    import re
    from difflib import SequenceMatcher
    
    try:
        student_name = request.data.get('student_name', '').strip()
        section_id = request.data.get('section_id')
        
        # 1. التحقق من صحة المدخلات
        if not student_name:
            return Response({
                'success': False,
                'error': 'missing_name',
                'message': 'يرجى إدخال الاسم الكامل'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not section_id:
            return Response({
                'success': False,
                'error': 'missing_section',
                'message': 'معرف الشعبة مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. التحقق من صحة الاسم (رباعي + عربي)
        name_parts = student_name.split()
        if len(name_parts) < 4:
            return Response({
                'success': False,
                'error': 'invalid_name_format',
                'message': f'الاسم يجب أن يكون رباعياً ({len(name_parts)}/4 أجزاء)',
                'suggestion': 'مثال: محمد أحمد علي حسن'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من الحروف العربية فقط
        arabic_pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
        if not arabic_pattern.match(student_name):
            return Response({
                'success': False,
                'error': 'invalid_name_characters',
                'message': 'الاسم يجب أن يحتوي على حروف عربية فقط',
                'suggestion': 'تأكد من عدم وجود أرقام أو رموز'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. تطبيع الاسم
        def normalize_arabic_name(name):
            name = ' '.join(name.split())
            name = re.sub('[إأآا]', 'ا', name)
            name = re.sub('ى', 'ي', name)
            name = re.sub('ة', 'ه', name)
            return name.strip().lower()
        
        normalized_name = normalize_arabic_name(student_name)
        
        # 4. البحث عن الشعبة
        try:
            section = Section.objects.select_related('grade').get(id=section_id)
        except Section.DoesNotExist:
            return Response({
                'success': False,
                'error': 'section_not_found',
                'message': 'الشعبة غير موجودة'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 5. البحث عن الطالب في هذه الشعبة
        students = StudentRegistration.objects.filter(
            section=section,
            normalized_name=normalized_name
        )
        
        # 6. إذا لم يُوجد، البحث بالتشابه
        if not students.exists():
            all_students = StudentRegistration.objects.filter(section=section)
            
            similar_students = []
            for student in all_students:
                similarity = SequenceMatcher(
                    None, 
                    normalized_name, 
                    student.normalized_name
                ).ratio()
                
                if similarity >= 0.75:  # 75% تشابه
                    similar_students.append({
                        'name': student.full_name,
                        'similarity': round(similarity * 100, 1)
                    })
            
            # ترتيب حسب التشابه
            similar_students.sort(key=lambda x: x['similarity'], reverse=True)
            
            return Response({
                'success': False,
                'error': 'student_not_found',
                'message': 'الاسم غير موجود في هذه الشعبة',
                'suggestions': similar_students[:3] if similar_students else [],
                'action': 'تواصل مع معلمك لإضافة اسمك' if not similar_students else 'هل تقصد أحد هذه الأسماء؟'
            }, status=status.HTTP_404_NOT_FOUND)
        
        student = students.first()
        
        # 7. جلب معلومات القروب
        telegram_group = None
        try:
            telegram_group = TelegramGroup.objects.get(section=section)
        except TelegramGroup.DoesNotExist:
            return Response({
                'success': False,
                'error': 'telegram_group_not_found',
                'message': 'قروب التليجرام غير موجود لهذه الشعبة',
                'action': 'تواصل مع معلمك'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 8. نجح التحقق - إرجاع البيانات
        return Response({
            'success': True,
            'student': {
                'id': student.id,
                'name': student.full_name,
                'grade': student.grade.display_name if student.grade else '-',
                'section': student.section.section_name,
                'school': student.school_name or section.grade.school_name
            },
            'telegram_group': {
                'name': telegram_group.group_name,
                'invite_link': telegram_group.invite_link,
                'chat_id': telegram_group.chat_id
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error in verify_student_for_join: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': 'server_error',
            'message': 'حدث خطأ أثناء التحقق. يرجى المحاولة مرة أخرى'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_promote_bot_in_groups(request):
    """
    ترقية البوت تلقائياً في جميع القروبات
    
    POST /api/sections/telegram/auto-promote-bot/
    """
    try:
        import subprocess
        import sys
        from django.conf import settings
        
        # مسار السكريبت
        script_path = os.path.join(settings.BASE_DIR.parent, 'auto_promote_bot.py')
        
        if not os.path.exists(script_path):
            return Response({
                'success': False,
                'error': 'السكريبت غير موجود'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # تشغيل السكريبت
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 دقائق
        )
        
        if result.returncode == 0:
            return Response({
                'success': True,
                'message': 'تمت ترقية البوت بنجاح',
                'output': result.stdout
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'فشل تشغيل السكريبت',
                'output': result.stderr or result.stdout
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except subprocess.TimeoutExpired:
        return Response({
            'success': False,
            'error': 'انتهت مهلة التنفيذ'
        }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
    except Exception as e:
        logger.error(f"Error in auto_promote_bot: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # يستدعيه Telegram Bot
def confirm_student_joined_telegram(request):
    """
    تأكيد انضمام الطالب إلى قروب Telegram
    يُستدعى من Bot عندما ينضم الطالب للقروب
    
    Request Body:
    {
        "student_id": 6,
        "telegram_user_id": 123456789,
        "telegram_username": "student_username",
        "chat_id": -1001234567890
    }
    """
    try:
        student_id = request.data.get('student_id')
        telegram_user_id = request.data.get('telegram_user_id')
        telegram_username = request.data.get('telegram_username', '')
        chat_id = request.data.get('chat_id')
        
        # التحقق من المدخلات
        if not student_id or not telegram_user_id:
            return Response({
                'success': False,
                'error': 'missing_data',
                'message': 'student_id و telegram_user_id مطلوبان'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # جلب الطالب
        try:
            student = StudentRegistration.objects.get(id=student_id)
        except StudentRegistration.DoesNotExist:
            return Response({
                'success': False,
                'error': 'student_not_found',
                'message': 'الطالب غير موجود'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # تحديث البيانات
        student.joined_telegram = True
        student.telegram_user_id = telegram_user_id
        student.telegram_username = telegram_username
        student.joined_at = timezone.now()
        student.save()
        
        logger.info(f"✅ الطالب {student.full_name} (ID: {student_id}) انضم إلى Telegram (user_id: {telegram_user_id})")
        
        return Response({
            'success': True,
            'message': 'تم تحديث بيانات الطالب بنجاح',
            'student': {
                'id': student.id,
                'name': student.full_name,
                'joined_telegram': True,
                'joined_at': student.joined_at.isoformat()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error in confirm_student_joined_telegram: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': 'server_error',
            'message': 'حدث خطأ أثناء التحديث'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== إضافة الطلاب (يدوي / Excel) ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_students_manually(request):
    """
    إضافة طلاب يدوياً إلى شعبة
    
    Request Body:
    {
        "section_id": 6,
        "students": [
            {
                "full_name": "محمد أحمد علي حسن",
                "phone": "0501234567"
            }
        ]
    }
    """
    import re
    
    try:
        teacher = get_teacher_from_request(request)
        
        section_id = request.data.get('section_id')
        students_data = request.data.get('students', [])
        
        # التحقق من المدخلات
        if not section_id:
            return Response({
                'success': False,
                'error': 'missing_section',
                'message': 'معرف الشعبة مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not students_data or not isinstance(students_data, list):
            return Response({
                'success': False,
                'error': 'invalid_data',
                'message': 'قائمة الطلاب مطلوبة'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من ملكية الشعبة
        try:
            section = Section.objects.select_related('grade').get(
                id=section_id,
                grade__teacher=teacher
            )
        except Section.DoesNotExist:
            return Response({
                'success': False,
                'error': 'section_not_found',
                'message': 'الشعبة غير موجودة أو ليس لديك صلاحية'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # دالة تطبيع الأسماء
        def normalize_arabic_name(name):
            name = ' '.join(name.split())
            name = re.sub('[إأآا]', 'ا', name)
            name = re.sub('ى', 'ي', name)
            name = re.sub('ة', 'ه', name)
            return name.strip().lower()
        
        # معالجة كل طالب
        added_students = []
        errors = []
        duplicates = []
        
        for idx, student_data in enumerate(students_data, 1):
            full_name = student_data.get('full_name', '').strip()
            phone = student_data.get('phone', '').strip()
            
            # التحقق من صحة البيانات
            validation_errors = []
            
            # التحقق من الاسم
            if not full_name:
                validation_errors.append('الاسم مطلوب')
            else:
                name_parts = full_name.split()
                if len(name_parts) < 4:
                    validation_errors.append(f'الاسم يجب أن يكون رباعياً ({len(name_parts)}/4)')
                
                arabic_pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
                if not arabic_pattern.match(full_name):
                    validation_errors.append('الاسم يجب أن يكون بالعربية فقط')
            
            # التحقق من رقم الجوال
            if not phone:
                validation_errors.append('رقم الجوال مطلوب')
            else:
                # إزالة المسافات والرموز
                phone_clean = re.sub(r'[^\d+]', '', phone)
                
                # التحقق من الطول (10 أرقام للسعودية)
                if not re.match(r'^(05|5)\d{8}$', phone_clean.replace('+966', '')):
                    validation_errors.append('رقم الجوال غير صحيح (يجب أن يبدأ بـ 05 ويكون 10 أرقام)')
                
                # توحيد الصيغة
                phone = phone_clean.replace('+966', '0') if phone_clean.startswith('+966') else phone_clean
                phone = '0' + phone if phone.startswith('5') else phone
            
            if validation_errors:
                errors.append({
                    'index': idx,
                    'name': full_name,
                    'phone': phone,
                    'errors': validation_errors
                })
                continue
            
            # التحقق من التكرار في قاعدة البيانات
            normalized_name = normalize_arabic_name(full_name)
            existing = StudentRegistration.objects.filter(
                section=section,
                normalized_name=normalized_name
            ).first()
            
            if existing:
                duplicates.append({
                    'index': idx,
                    'name': full_name,
                    'phone': phone,
                    'existing_phone': existing.phone_number or 'غير محدد'
                })
                continue
            
            # إضافة الطالب
            try:
                student = StudentRegistration.objects.create(
                    full_name=full_name,
                    normalized_name=normalized_name,
                    phone_number=phone,
                    teacher=teacher,  # ✅ FIX: Add missing teacher field
                    section=section,
                    grade=section.grade,
                    school_name=section.grade.school_name,
                    registration_ip=request.META.get('REMOTE_ADDR', ''),
                    joined_telegram=False
                )
                
                added_students.append({
                    'id': student.id,
                    'name': student.full_name,
                    'phone': student.phone_number
                })
                
                logger.info(f"✅ تم إضافة الطالب: {full_name} إلى الشعبة {section.id}")
                
            except Exception as e:
                logger.error(f"❌ خطأ في إضافة الطالب {full_name}: {str(e)}")
                errors.append({
                    'index': idx,
                    'name': full_name,
                    'phone': phone,
                    'errors': [f'خطأ في الحفظ: {str(e)}']
                })
        
        # ✅ تحديث عدد الطلاب في الشعبة
        if added_students:
            section.total_students = section.registered_students.count()
            section.save()
            logger.info(f"✅ تم تحديث total_students للشعبة {section.id}: {section.total_students}")
        
        # الإحصائيات
        stats = {
            'total': len(students_data),
            'added': len(added_students),
            'errors': len(errors),
            'duplicates': len(duplicates)
        }
        
        return Response({
            'success': True,
            'message': f'تم إضافة {len(added_students)} طالب بنجاح',
            'stats': stats,
            'added_students': added_students,
            'errors': errors,
            'duplicates': duplicates
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"❌ Error in add_students_manually: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': 'server_error',
            'message': 'حدث خطأ أثناء إضافة الطلاب'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_students_excel(request):
    """
    رفع ملف Excel يحتوي على الطلاب
    
    Request:
    - multipart/form-data
    - file: Excel file
    - section_id: int
    """
    try:
        import pandas as pd
        import re
        
        teacher = get_teacher_from_request(request)
        
        section_id = request.data.get('section_id')
        excel_file = request.FILES.get('file')
        
        # التحقق من المدخلات
        if not section_id:
            return Response({
                'success': False,
                'error': 'missing_section',
                'message': 'معرف الشعبة مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not excel_file:
            return Response({
                'success': False,
                'error': 'missing_file',
                'message': 'يرجى رفع ملف Excel'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من نوع الملف
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            return Response({
                'success': False,
                'error': 'invalid_file_type',
                'message': 'يجب أن يكون الملف من نوع Excel (.xlsx أو .xls)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من ملكية الشعبة
        try:
            section = Section.objects.select_related('grade').get(
                id=section_id,
                grade__teacher=teacher
            )
        except Section.DoesNotExist:
            return Response({
                'success': False,
                'error': 'section_not_found',
                'message': 'الشعبة غير موجودة أو ليس لديك صلاحية'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # قراءة ملف Excel
        try:
            df = pd.read_excel(excel_file, header=None)
            
            # التحقق من وجود عمودين على الأقل
            if df.shape[1] < 2:
                return Response({
                    'success': False,
                    'error': 'invalid_format',
                    'message': 'الملف يجب أن يحتوي على عمودين: الاسم ورقم الجوال'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # تسمية الأعمدة
            df.columns = ['full_name', 'phone'] + [f'col_{i}' for i in range(2, df.shape[1])]
            
            # إزالة الصفوف الفارغة
            df = df.dropna(subset=['full_name', 'phone'])
            
            # تحويل لقائمة
            students_data = []
            for idx, row in df.iterrows():
                students_data.append({
                    'full_name': str(row['full_name']).strip(),
                    'phone': str(row['phone']).strip()
                })
            
            if not students_data:
                return Response({
                    'success': False,
                    'error': 'empty_file',
                    'message': 'الملف لا يحتوي على بيانات'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"📊 تم قراءة {len(students_data)} سجل من ملف Excel")
            
            # معالجة البيانات باستخدام نفس منطق الإضافة اليدوية
            def normalize_arabic_name(name):
                name = ' '.join(name.split())
                name = re.sub('[إأآا]', 'ا', name)
                name = re.sub('ى', 'ي', name)
                name = re.sub('ة', 'ه', name)
                return name.strip().lower()
            
            added_students = []
            errors = []
            duplicates = []
            
            for idx, student_data in enumerate(students_data, 1):
                full_name = student_data['full_name']
                phone = student_data['phone']
                
                # التحقق من صحة البيانات
                validation_errors = []
                
                # التحقق من الاسم
                if not full_name or full_name == 'nan':
                    validation_errors.append('الاسم مطلوب')
                else:
                    name_parts = full_name.split()
                    if len(name_parts) < 4:
                        validation_errors.append(f'الاسم يجب أن يكون رباعياً ({len(name_parts)}/4)')
                    
                    arabic_pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
                    if not arabic_pattern.match(full_name):
                        validation_errors.append('الاسم يجب أن يكون بالعربية فقط')
                
                # التحقق من رقم الجوال
                if not phone or phone == 'nan':
                    validation_errors.append('رقم الجوال مطلوب')
                else:
                    phone_clean = re.sub(r'[^\d+]', '', str(phone))
                    
                    if not re.match(r'^(05|5)\d{8}$', phone_clean.replace('+966', '')):
                        validation_errors.append('رقم الجوال غير صحيح')
                    
                    phone = phone_clean.replace('+966', '0') if phone_clean.startswith('+966') else phone_clean
                    phone = '0' + phone if phone.startswith('5') else phone
                
                if validation_errors:
                    errors.append({
                        'row': idx,
                        'name': full_name,
                        'phone': phone,
                        'errors': validation_errors
                    })
                    continue
                
                # التحقق من التكرار
                normalized_name = normalize_arabic_name(full_name)
                existing = StudentRegistration.objects.filter(
                    section=section,
                    normalized_name=normalized_name
                ).first()
                
                if existing:
                    duplicates.append({
                        'row': idx,
                        'name': full_name,
                        'phone': phone,
                        'existing_phone': existing.phone_number or 'غير محدد'
                    })
                    continue
                
                # إضافة الطالب
                try:
                    student = StudentRegistration.objects.create(
                        full_name=full_name,
                        normalized_name=normalized_name,
                        phone_number=phone,
                        teacher=teacher,  # ✅ FIX: Add missing teacher field
                        section=section,
                        grade=section.grade,
                        school_name=section.grade.school_name,
                        registration_ip=request.META.get('REMOTE_ADDR', ''),
                        joined_telegram=False
                    )
                    
                    added_students.append({
                        'id': student.id,
                        'name': student.full_name,
                        'phone': student.phone_number
                    })
                    
                except Exception as e:
                    errors.append({
                        'row': idx,
                        'name': full_name,
                        'phone': phone,
                        'errors': [f'خطأ في الحفظ: {str(e)}']
                    })
            
            # ✅ تحديث عدد الطلاب في الشعبة
            if added_students:
                section.total_students = section.registered_students.count()
                section.save()
                logger.info(f"✅ تم تحديث total_students للشعبة {section.id}: {section.total_students}")
            
            stats = {
                'total': len(students_data),
                'added': len(added_students),
                'errors': len(errors),
                'duplicates': len(duplicates)
            }
            
            logger.info(f"✅ تم إضافة {len(added_students)} طالب من Excel")
            
            return Response({
                'success': True,
                'message': f'تم معالجة {len(students_data)} سجل، تم إضافة {len(added_students)} طالب',
                'stats': stats,
                'added_students': added_students,
                'errors': errors,
                'duplicates': duplicates
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"❌ خطأ في قراءة ملف Excel: {str(e)}")
            return Response({
                'success': False,
                'error': 'excel_error',
                'message': f'خطأ في قراءة الملف: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"❌ Error in upload_students_excel: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': 'server_error',
            'message': 'حدث خطأ أثناء رفع الملف'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_excel_template(request):
    """
    تحميل نموذج Excel فارغ
    """
    try:
        import pandas as pd
        from django.http import HttpResponse
        import io
        
        # إنشاء DataFrame مع أمثلة
        data = {
            'الاسم الرباعي': ['محمد أحمد علي حسن', 'فاطمة علي محمد حسن', 'أحمد خالد عبدالله سالم'],
            'رقم الجوال': ['0501234567', '0509876543', '0557654321']
        }
        
        df = pd.DataFrame(data)
        
        # حفظ في buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='الطلاب')
        
        output.seek(0)
        
        # إرجاع كـ response
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="template_students.xlsx"'
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in download_excel_template: {str(e)}")
        return Response({
            'success': False,
            'error': 'server_error',
            'message': 'حدث خطأ أثناء تحميل النموذج'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_dependencies(request):
    """
    التحقق من المكتبات المثبتة
    """
    import sys
    import pkg_resources
    
    dependencies_status = {}
    
    # قائمة المكتبات المطلوبة
    required_packages = [
        'telethon',
        'cryptg',
        'python-telegram-bot',
        'django',
        'djangorestframework',
        'psycopg',
        'google-generativeai'
    ]
    
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            dependencies_status[package] = {
                'installed': True,
                'version': version
            }
        except pkg_resources.DistributionNotFound:
            dependencies_status[package] = {
                'installed': False,
                'version': None
            }
    
    # فحص telethon بشكل خاص
    telethon_import_status = False
    try:
        import telethon
        telethon_import_status = True
    except ImportError:
        pass
    
    return Response({
        'success': True,
        'python_version': sys.version,
        'dependencies': dependencies_status,
        'telethon_importable': telethon_import_status
    }, status=status.HTTP_200_OK)
