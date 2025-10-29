"""
Views for Project Creation
Updated: 2025-10-24 22:42 - Force reload
"""
import os
import logging
import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Project, ProjectFile
from .serializers_new import (
    ProjectCreateSerializer, 
    ProjectListSerializer, 
    ProjectDetailSerializer
)
from apps.sections.models import Section
from apps.accounts.models import Teacher

logger = logging.getLogger(__name__)


def parse_array_field(request, field_name, convert_to_int=False):
    """
    Parse array field from FormData - supports both methods:
    1. Native FormData arrays: field=1&field=2&field=3
    2. JSON strings: field=[1,2,3]
    
    Args:
        request: Django request object
        field_name: Name of the field to parse
        convert_to_int: If True, convert values to integers
    
    Returns:
        List of parsed values
    """
    # Try getlist first (native FormData arrays)
    values = request.data.getlist(field_name, None)
    
    if values and len(values) > 1:
        # Multiple values found - native FormData approach
        logger.info(f"✅ {field_name} from getlist (native): {values}")
        try:
            if convert_to_int:
                return [int(v) for v in values if v and str(v).strip()]
            return [str(v).strip() for v in values if v and str(v).strip()]
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Failed to convert {field_name} values: {e}")
            return []
    
    # Try single value (might be JSON string)
    single_value = request.data.get(field_name, None)
    
    if single_value:
        # Check if it's a JSON string
        if isinstance(single_value, str) and single_value.strip().startswith('['):
            try:
                import json
                parsed = json.loads(single_value)
                logger.info(f"✅ {field_name} from JSON string: {parsed}")
                if convert_to_int:
                    return [int(v) for v in parsed if v]
                return [str(v).strip() for v in parsed if v and str(v).strip()]
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse {field_name} JSON: {e}")
                return []
        # Single non-JSON value (edge case)
        elif isinstance(single_value, list):
            logger.info(f"✅ {field_name} from direct list: {single_value}")
            if convert_to_int:
                return [int(v) for v in single_value if v]
            return [str(v).strip() for v in single_value if v and str(v).strip()]
    
    logger.warning(f"⚠️ {field_name} not found or empty")
    return []


def get_teacher_from_request(request):
    """Helper to get teacher from request"""
    try:
        return Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_project(request):
    """
    Create a new project
    
    POST /api/projects/create/
    Content-Type: multipart/form-data
    
    Form Fields:
    - title, subject, description
    - grade_id, section_ids (JSON array)
    - instructions, requirements, tips
    - settings (JSON object)
    - video (file), pdfs (files), docs (files)
    - video_link, links (JSON array)
    """
    
    teacher = get_teacher_from_request(request)
    if not teacher:
        return Response({
            'error': 'المعلم غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Parse data
        import json
        
        # ⚠️ CRITICAL DEBUG: Log RAW request data
        logger.info("=" * 80)
        logger.info("🔍 RAW REQUEST DATA:")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"request.data type: {type(request.data)}")
        
        # Log all fields
        for key in request.data.keys():
            value = request.data.get(key)
            value_list = request.data.getlist(key, None)
            logger.info(f"  {key}:")
            logger.info(f"    - get(): {value} (type: {type(value)})")
            logger.info(f"    - getlist(): {value_list}")
        logger.info("=" * 80)
        
        # Parse JSON fields if they're strings
        data = request.data.copy()
        
        # Parse section_ids using helper function
        data['section_ids'] = parse_array_field(request, 'section_ids', convert_to_int=True)
        
        # Fallback: try 'sections' field if section_ids is empty
        if not data['section_ids'] and 'sections' in data:
            data['section_ids'] = parse_array_field(request, 'sections', convert_to_int=True)
        
        # Parse allowed_file_types using helper function
        data['allowed_file_types'] = parse_array_field(request, 'allowed_file_types', convert_to_int=False)
        
        # Parse settings
        if 'settings' in data and isinstance(data['settings'], str):
            try:
                settings_data = json.loads(data['settings'])
                data.update(settings_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Parse external_links using helper function
        data['external_links'] = parse_array_field(request, 'external_links', convert_to_int=False)
        
        # Fallback: try 'links' field if external_links is empty
        if not data['external_links'] and 'links' in data:
            data['external_links'] = parse_array_field(request, 'links', convert_to_int=False)
        
        # Ensure external_links is always a list (even if empty)
        if 'external_links' not in data:
            data['external_links'] = []
        
        # Log parsed data for debugging
        logger.info("=" * 80)
        logger.info("📊 PARSED DATA BEFORE VALIDATION:")
        logger.info(f"  section_ids: {data.get('section_ids')} (type: {type(data.get('section_ids'))}, length: {len(data.get('section_ids', []))})")
        logger.info(f"  allowed_file_types: {data.get('allowed_file_types')} (type: {type(data.get('allowed_file_types'))}, length: {len(data.get('allowed_file_types', []))})")
        logger.info(f"  external_links: {data.get('external_links')} (type: {type(data.get('external_links'))}, length: {len(data.get('external_links', []))})")
        logger.info(f"  grade_id: {data.get('grade_id')} (type: {type(data.get('grade_id'))})")
        logger.info("=" * 80)
        
        # Validate data
        serializer = ProjectCreateSerializer(data=data)
        if not serializer.is_valid():
            logger.error("=" * 80)
            logger.error("❌ SERIALIZER VALIDATION FAILED:")
            logger.error(f"Errors: {serializer.errors}")
            logger.error("=" * 80)
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        # Create project
        project = Project.objects.create(
            teacher=teacher,
            title=validated_data['title'],
            subject=validated_data['subject'],
            description=validated_data.get('description', ''),
            instructions=validated_data['instructions'],
            requirements=validated_data['requirements'],
            tips=validated_data.get('tips', ''),
            start_date=validated_data['start_date'],
            deadline=validated_data['deadline'],
            max_file_size=validated_data['max_file_size'],
            allowed_file_types=validated_data['allowed_file_types'],
            max_grade=validated_data['max_grade'],
            allow_late_submission=validated_data['allow_late_submission'],
            send_reminder=validated_data['send_reminder'],
            ai_check_plagiarism=validated_data['ai_check_plagiarism'],
            ai_enhanced=True  # Since we're using AI to generate tips
        )
        
        # Add sections
        section_ids = validated_data['section_ids']
        sections = Section.objects.filter(id__in=section_ids)
        project.sections.add(*sections)
        
        # Handle files
        files_saved = handle_project_files(request, project)
        
        # Send to Telegram
        telegram_results = send_project_to_telegram(project)
        project.telegram_sent = telegram_results.get('success_count', 0) > 0 if telegram_results else False
        project.save()
        
        # Return response
        return Response({
            'success': True,
            'project_id': project.id,
            'title': project.title,
            'sections_count': project.sections.count(),
            'files_count': project.files.count(),
            'telegram_sent': project.telegram_sent,
            'telegram_results': telegram_results,  # ✅ إرجاع النتائج الكاملة
            'message': 'تم إنشاء المشروع وإرساله بنجاح' if project.telegram_sent else 'تم إنشاء المشروع بنجاح'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}", exc_info=True)
        return Response({
            'error': 'حدث خطأ أثناء إنشاء المشروع',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_project_files(request, project):
    """Handle file uploads for project"""
    files_saved = []
    
    try:
        # Video file
        if 'video' in request.FILES:
            video = request.FILES['video']
            file_path = save_file(video, 'projects/videos')
            
            ProjectFile.objects.create(
                project=project,
                file_type='video',
                file_path=file_path,
                file_name=video.name,
                file_size=video.size
            )
            files_saved.append('video')
        
        # Video link
        if 'videoLink' in request.data or 'video_link' in request.data:
            video_link = request.data.get('videoLink') or request.data.get('video_link')
            if video_link:
                ProjectFile.objects.create(
                    project=project,
                    file_type='video',
                    external_link=video_link
                )
                files_saved.append('video_link')
        
        # PDF files
        if 'pdfs' in request.FILES:
            pdfs = request.FILES.getlist('pdfs')
            for pdf in pdfs[:5]:  # Max 5 files
                file_path = save_file(pdf, 'projects/pdfs')
                ProjectFile.objects.create(
                    project=project,
                    file_type='pdf',
                    file_path=file_path,
                    file_name=pdf.name,
                    file_size=pdf.size
                )
            files_saved.append(f'{len(pdfs)} PDFs')
        
        # Office docs
        if 'docs' in request.FILES:
            docs = request.FILES.getlist('docs')
            for doc in docs[:5]:  # Max 5 files
                file_path = save_file(doc, 'projects/docs')
                ProjectFile.objects.create(
                    project=project,
                    file_type='doc',
                    file_path=file_path,
                    file_name=doc.name,
                    file_size=doc.size
                )
            files_saved.append(f'{len(docs)} Office')
        
        # External links
        if 'external_links' in request.data:
            links = request.data['external_links']
            if isinstance(links, list):
                for link in links:
                    ProjectFile.objects.create(
                        project=project,
                        file_type='link',
                        external_link=link
                    )
                files_saved.append(f'{len(links)} links')
        
        logger.info(f"Files saved for project {project.id}: {files_saved}")
        return files_saved
        
    except Exception as e:
        logger.error(f"Error handling files: {str(e)}")
        return files_saved


def save_file(uploaded_file, subfolder):
    """Save uploaded file and return path"""
    import hashlib
    from datetime import datetime
    
    # Create directory
    base_dir = os.path.join(settings.MEDIA_ROOT, subfolder)
    os.makedirs(base_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(uploaded_file.name)
    filename = f"{timestamp}_{hashlib.md5(name.encode()).hexdigest()[:8]}{ext}"
    
    # Save file
    file_path = os.path.join(base_dir, filename)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    # Return relative path
    return os.path.join(subfolder, filename)


def send_project_to_telegram(project):
    """
    Send project notification to Telegram groups
    Returns: dict with success/failed lists and statistics
    """
    try:
        from .telegram_helper import telegram_notifier
        
        # Get full results dict from telegram_helper
        results = telegram_notifier.send_project_notification(project)
        
        logger.info(f"Telegram notification: {results.get('success_count', 0)} succeeded, {results.get('failed_count', 0)} failed")
        
        return results
        
    except Exception as e:
        logger.error(f"Error sending to Telegram: {str(e)}")
        return {
            'success': [],
            'failed': [],
            'total': 0,
            'success_count': 0,
            'failed_count': 0,
            'error': str(e)
        }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_projects(request):
    """List teacher's projects"""
    
    teacher = get_teacher_from_request(request)
    if not teacher:
        return Response({
            'error': 'المعلم غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    
    projects = Project.objects.filter(teacher=teacher, is_active=True)
    serializer = ProjectListSerializer(projects, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_detail(request, project_id):
    """Get project details"""
    
    teacher = get_teacher_from_request(request)
    if not teacher:
        return Response({
            'error': 'المعلم غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Fetch project with all related data for better performance
        project = Project.objects.prefetch_related(
            'files',  # Fetch all project files
            'sections__grade',  # Fetch sections with grades
            'sections__telegram_group'  # Fetch telegram groups if needed
        ).get(id=project_id, teacher=teacher)
        
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Project.DoesNotExist:
        return Response({
            'error': 'المشروع غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"❌ Error in project_detail: {str(e)}", exc_info=True)
        return Response({
            'error': 'حدث خطأ أثناء تحميل المشروع',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request, project_id):
    """Delete project (soft delete)"""
    
    teacher = get_teacher_from_request(request)
    if not teacher:
        return Response({
            'error': 'المعلم غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        project = Project.objects.get(id=project_id, teacher=teacher)
        project.is_active = False
        project.save()
        
        return Response({
            'message': 'تم حذف المشروع بنجاح'
        }, status=status.HTTP_200_OK)
        
    except Project.DoesNotExist:
        return Response({
            'error': 'المشروع غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])  # لا يحتاج authentication
def project_detail_public(request, project_id):
    """
    Get project details via JWT token (for students submitting projects)
    No authentication required, but validates JWT token from query params
    """
    
    try:
        # Get token from query parameters or headers
        token = request.query_params.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        
        if token:
            try:
                # Verify JWT token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                
                # Verify project_id matches token
                if payload.get('project_id') != project_id:
                    return Response({
                        'error': 'رابط غير صالح'
                    }, status=status.HTTP_403_FORBIDDEN)
                
            except jwt.ExpiredSignatureError:
                return Response({
                    'error': 'الرابط منتهي الصلاحية'
                }, status=status.HTTP_403_FORBIDDEN)
            except jwt.InvalidTokenError:
                return Response({
                    'error': 'رابط غير صالح'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Get project
        project = Project.objects.select_related('teacher').prefetch_related('sections').get(id=project_id)
        
        # Serialize project data
        serializer = ProjectDetailSerializer(project)
        
        return Response({
            'success': True,
            'project': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Project.DoesNotExist:
        return Response({
            'error': 'المشروع غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
