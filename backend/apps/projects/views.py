"""
Views for Projects App
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from apps.accounts.models import Teacher
from .models import Project, Student, Group, Submission
from .serializers import (
    ProjectSerializer, StudentSerializer, GroupSerializer,
    SubmissionSerializer, SubmissionReviewSerializer
)
from utils.storage import secure_upload
import logging

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def project_list_create(request):
    """الحصول على قائمة المشاريع أو إنشاء مشروع جديد"""
    try:
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            projects = Project.objects.filter(teacher=teacher).prefetch_related(
                'sections__grade',  # Load sections with their grades
                'sections__telegram_group'  # Load telegram groups too
            ).order_by('-created_at')
            
            serializer = ProjectSerializer(projects, many=True)
            
            return Response({
                'projects': serializer.data,
                'count': projects.count()
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            serializer = ProjectSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'error': 'بيانات غير صحيحة',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            project = serializer.save(teacher=teacher)
            
            logger.info(f"Project created: {project.title} by {teacher.email}")
            
            return Response({
                'message': 'تم إنشاء المشروع بنجاح',
                'project': ProjectSerializer(project).data
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in project_list_create: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def project_detail(request, pk):
    """الحصول على/تحديث/حذف مشروع"""
    try:
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        project = Project.objects.filter(pk=pk, teacher=teacher).first()
        
        if not project:
            return Response({
                'error': 'لم يتم العثور على المشروع'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            return Response({
                'project': ProjectSerializer(project).data
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return Response({
                    'error': 'بيانات غير صحيحة',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            
            logger.info(f"Project updated: {project.title}")
            
            return Response({
                'message': 'تم تحديث المشروع بنجاح',
                'project': serializer.data
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            project_title = project.title
            project.delete()
            
            logger.info(f"Project deleted: {project_title}")
            
            return Response({
                'message': 'تم حذف المشروع بنجاح'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in project_detail: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def student_list_create(request, project_id):
    """الحصول على قائمة الطلاب أو إضافة طالب"""
    try:
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        project = Project.objects.filter(pk=project_id, teacher=teacher).first()
        
        if not project:
            return Response({
                'error': 'لم يتم العثور على المشروع'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            students = Student.objects.filter(project=project)
            serializer = StudentSerializer(students, many=True)
            
            return Response({
                'students': serializer.data,
                'count': students.count()
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            serializer = StudentSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'error': 'بيانات غير صحيحة',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            student = serializer.save(project=project)
            
            logger.info(f"Student added: {student.student_name} to project {project.title}")
            
            return Response({
                'message': 'تم إضافة الطالب بنجاح',
                'student': StudentSerializer(student).data
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in student_list_create: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_submission(request):
    """رفع تسليم مشروع مع التحقق المتقدم"""
    try:
        # الحصول على البيانات
        project_id = request.data.get('project_id')
        student_id = request.data.get('student_id')
        group_id = request.data.get('group_id')
        uploaded_file = request.FILES.get('file')
        submit_token = request.data.get('submit_token')  # رمز التسليم
        
        if not uploaded_file:
            return Response({
                'error': 'لم يتم رفع أي ملف'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not project_id:
            return Response({
                'error': 'معرف المشروع مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من submit_token
        if submit_token:
            from apps.otp_system.models import ProjectOTP
            try:
                otp_record = ProjectOTP.objects.get(
                    submit_token=submit_token,
                    status='verified',
                    project_id=project_id,
                    submit_token_expires__gt=timezone.now()
                )
                # تحديد الرمز كمستخدم
                otp_record.mark_as_used()
                
            except ProjectOTP.DoesNotExist:
                return Response({
                    'error': 'رمز التسليم غير صالح أو منتهي'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # البحث عن المشروع
        project = Project.objects.filter(pk=project_id).first()
        
        if not project:
            return Response({
                'error': 'لم يتم العثور على المشروع'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # التحقق من نشاط المشروع
        if not project.is_active:
            return Response({
                'error': 'المشروع غير نشط'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من الموعد النهائي
        if timezone.now() > project.deadline:
            return Response({
                'error': 'انتهى الموعد النهائي للتسليم'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # البحث عن الطالب أو المجموعة
        student = None
        group = None
        
        if student_id:
            student = Student.objects.filter(pk=student_id, project=project).first()
            if not student:
                return Response({
                    'error': 'لم يتم العثور على الطالب'
                }, status=status.HTTP_404_NOT_FOUND)
        
        if group_id:
            group = Group.objects.filter(pk=group_id, project=project).first()
            if not group:
                return Response({
                    'error': 'لم يتم العثور على المجموعة'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # ===== التحقق المتقدم من الملف =====
        from apps.projects.utils import FileValidator
        
        validator = FileValidator(uploaded_file, project)
        validation_result = validator.validate_all()
        
        # إذا كانت هناك أخطاء، نرفض الملف
        if not validation_result['valid']:
            logger.warning(f"File validation failed: {uploaded_file.name}")
            return Response({
                'error': 'الملف لا يستوفي الشروط',
                'validation': {
                    'errors': validation_result['errors'],
                    'warnings': validation_result['warnings']
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # رفع الملف بشكل آمن
        result = secure_upload.save_file(uploaded_file, subfolder=f'projects/{project_id}')
        
        if not result['success']:
            return Response({
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # إنشاء سجل التسليم
        submission = Submission.objects.create(
            project=project,
            group=group,
            student=student,
            file_path=result['file_path'],
            file_name=uploaded_file.name,
            file_size=uploaded_file.size,
            file_type=uploaded_file.content_type,
            file_hash=validation_result['file_info']['hash'],
            validation_data=validation_result,
            # بيانات الفحص
            virus_scanned=validation_result['virus_scan'].get('scanned', False),
            virus_clean=validation_result['virus_scan'].get('clean', True),
            ai_checked=validation_result['ai_check'].get('checked', False) if validation_result['ai_check'] else False,
            ai_compliant=validation_result['ai_check'].get('compliant', True) if validation_result['ai_check'] else True,
            ai_confidence=validation_result['ai_check'].get('confidence', 0) if validation_result['ai_check'] else 0
        )
        
        logger.info(f"Submission uploaded: {uploaded_file.name} for project {project.title}")
        
        return Response({
            'message': 'تم رفع المشروع بنجاح',
            'submission': SubmissionSerializer(submission).data,
            'validation': {
                'virus_scan': validation_result['virus_scan'],
                'ai_check': validation_result['ai_check'],
                'warnings': validation_result['warnings']
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in upload_submission: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء رفع الملف',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def validate_file(request, project_id):
    """
    التحقق من الملف قبل الرفع (Preview)
    يعطي تقرير شامل عن الملف دون حفظه
    """
    try:
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            return Response({
                'error': 'لم يتم رفع أي ملف'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # البحث عن المشروع
        project = Project.objects.filter(pk=project_id).first()
        
        if not project:
            return Response({
                'error': 'لم يتم العثور على المشروع'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # التحقق من الملف
        from apps.projects.utils import FileValidator
        
        validator = FileValidator(uploaded_file, project)
        validation_result = validator.validate_all()
        
        return Response({
            'valid': validation_result['valid'],
            'file_info': validation_result['file_info'],
            'errors': validation_result['errors'],
            'warnings': validation_result['warnings'],
            'virus_scan': validation_result['virus_scan'],
            'ai_check': validation_result['ai_check']
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in validate_file: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء التحقق من الملف',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def submission_list(request, project_id):
    """الحصول على قائمة التسليمات"""
    try:
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        project = Project.objects.filter(pk=project_id, teacher=teacher).first()
        
        if not project:
            return Response({
                'error': 'لم يتم العثور على المشروع'
            }, status=status.HTTP_404_NOT_FOUND)
        
        submissions = Submission.objects.filter(project=project)
        serializer = SubmissionSerializer(submissions, many=True)
        
        return Response({
            'submissions': serializer.data,
            'count': submissions.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in submission_list: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def review_submission(request, submission_id):
    """مراجعة تسليم"""
    try:
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        submission = Submission.objects.filter(pk=submission_id, project__teacher=teacher).first()
        
        if not submission:
            return Response({
                'error': 'لم يتم العثور على التسليم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SubmissionReviewSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        submission.status = serializer.validated_data['status']
        submission.notes = serializer.validated_data.get('notes', '')
        submission.grade = serializer.validated_data.get('grade')
        submission.reviewed_at = timezone.now()
        submission.save()
        
        logger.info(f"Submission reviewed: {submission.file_name} - {submission.status}")
        
        return Response({
            'message': 'تم مراجعة التسليم بنجاح',
            'submission': SubmissionSerializer(submission).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in review_submission: {str(e)}")
        return Response({
            'error': 'حدث خطأ',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_project_telegram(request, project_id):
    """إرسال إشعار تليجرام لمشروع موجود"""
    try:
        # Get teacher
        email = request.user.email if hasattr(request.user, 'email') else request.auth.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        
        if not teacher:
            return Response({
                'error': 'لم يتم العثور على المعلم'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get project
        project = Project.objects.filter(
            id=project_id, 
            teacher=teacher
        ).prefetch_related('sections__telegram_group').first()
        
        if not project:
            return Response({
                'error': 'لم يتم العثور على المشروع'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Send Telegram notification
        from .telegram_helper import TelegramProjectNotifier
        
        logger.info(f"📱 Sending Telegram notification for project: {project.title}")
        
        notifier = TelegramProjectNotifier()
        result = notifier.send_project_notification(
            project, 
            send_files=request.data.get('send_files', True),
            pin_message=request.data.get('pin_message', True)
        )
        
        if result:
            telegram_results = {
                'success': result.get('success', []),
                'failed': result.get('failed', []),
                'total': result.get('total', 0),
                'sent': True
            }
            
            # Update project telegram_sent status
            if len(telegram_results['success']) > 0:
                project.telegram_sent = True
                project.save()
            
            logger.info(f"✅ Telegram sent to {len(telegram_results['success'])} sections")
            
            return Response({
                'success': True,
                'message': f'تم إرسال الإشعار إلى {len(telegram_results["success"])} شعبة',
                'telegram': telegram_results
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'فشل إرسال الإشعار',
                'details': 'لم يتم الحصول على نتائج'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"❌ Error sending Telegram: {str(e)}", exc_info=True)
        return Response({
            'error': 'حدث خطأ أثناء إرسال الإشعار',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def submit_project_with_ai(request, project_id):
    """
    استلام المشروع مع التحقق بالذكاء الاصطناعي
    """
    try:
        project = Project.objects.get(id=project_id, is_active=True)
        
        # 1. التحقق من البيانات الأساسية
        student_name = request.data.get('student_name')
        student_id = request.data.get('student_id')
        file = request.FILES.get('file')
        
        if not all([student_name, student_id, file]):
            return Response({
                'error': 'جميع الحقول مطلوبة (student_name, student_id, file)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. التحقق من عدد المحاولات
        previous_attempts = Submission.objects.filter(
            project=project,
            submitted_student_id=student_id
        ).count()
        
        if previous_attempts >= project.max_attempts:
            return Response({
                'error': f'لقد تجاوزت الحد الأقصى للمحاولات ({project.max_attempts})',
                'attempts': previous_attempts,
                'max_attempts': project.max_attempts
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. التحقق من الموعد النهائي
        if project.is_expired and not project.allow_late_submission:
            return Response({
                'error': 'انتهى موعد التسليم',
                'deadline': project.deadline
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 4. التحقق من نوع الملف
        import os
        file_extension = os.path.splitext(file.name)[1].lower().replace('.', '')
        allowed_formats = project.file_constraints.get('formats', []) or project.allowed_file_types
        
        if allowed_formats and file_extension not in allowed_formats:
            return Response({
                'error': f'نوع الملف غير مقبول. المسموح: {", ".join(allowed_formats)}',
                'file_type': file_extension,
                'allowed': allowed_formats
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 5. التحقق من الحجم
        max_size_mb = project.file_constraints.get('max_size_mb') or project.max_file_size
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file.size > max_size_bytes:
            return Response({
                'error': f'حجم الملف كبير جداً. الحد الأقصى: {max_size_mb} MB',
                'file_size': file.size / (1024 * 1024),  # MB
                'max_size': max_size_mb
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 6. حفظ الملف بشكل آمن
        upload_result = secure_upload(
            file,
            subfolder=f'projects/{project.id}',
            allowed_extensions=allowed_formats
        )
        
        if not upload_result['success']:
            return Response({
                'error': 'فشل رفع الملف',
                'details': upload_result.get('error', 'Unknown error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        file_path = upload_result['file_path']
        
        # 7. إنشاء Submission
        submission = Submission.objects.create(
            project=project,
            submitted_student_name=student_name,
            submitted_student_id=student_id,
            file_path=file_path,
            file_name=file.name,
            file_size=file.size,
            file_type=file_extension,
            attempt_number=previous_attempts + 1,
            validation_status='pending'
        )
        
        logger.info(f"✅ تم إنشاء Submission #{submission.id} للمشروع #{project.id}")
        
        # 8. إضافة للـ Queue للمعالجة بالـ AI
        if project.ai_validation_enabled:
            from .tasks import process_submission_with_ai
            process_submission_with_ai.delay(submission.id)
            
            message = 'تم رفع المشروع بنجاح. جاري التحليل بالذكاء الاصطناعي...'
        else:
            submission.validation_status = 'pending'
            submission.save()
            message = 'تم رفع المشروع بنجاح. في انتظار مراجعة المعلم.'
        
        return Response({
            'success': True,
            'message': message,
            'submission': {
                'id': submission.id,
                'attempt_number': submission.attempt_number,
                'remaining_attempts': project.max_attempts - submission.attempt_number,
                'status': submission.validation_status,
                'submitted_at': submission.submitted_at
            }
        }, status=status.HTTP_201_CREATED)
        
    except Project.DoesNotExist:
        return Response({
            'error': 'المشروع غير موجود أو غير نشط'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"❌ Error in submit_project_with_ai: {str(e)}", exc_info=True)
        return Response({
            'error': 'حدث خطأ أثناء رفع المشروع',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_submission_status_view(request, submission_id):
    """
    التحقق من حالة التسليم
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        
        response_data = {
            'submission_id': submission.id,
            'status': submission.validation_status,
            'ai_score': float(submission.ai_score) if submission.ai_score else None,
            'rejection_reasons': submission.rejection_reasons,
            'validation_results': submission.validation_results,
            'processing_time': submission.processing_time,
            'processed_at': submission.processed_at.isoformat() if submission.processed_at else None,
            'submitted_at': submission.submitted_at.isoformat(),
            'attempt_number': submission.attempt_number
        }
        
        # إضافة معلومات المشروع
        response_data['project'] = {
            'id': submission.project.id,
            'title': submission.project.title,
            'max_attempts': submission.project.max_attempts,
            'remaining_attempts': submission.project.max_attempts - submission.attempt_number
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Submission.DoesNotExist:
        return Response({
            'error': 'التسليم غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
