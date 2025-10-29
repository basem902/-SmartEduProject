"""
Project Creation API - Clean & Simple Version
Author: Cascade AI
Date: 2025-10-24
"""
import logging
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Project, ProjectFile
from .serializers_new import ProjectCreateSerializer
from apps.sections.models import Section
from apps.accounts.models import Teacher

logger = logging.getLogger(__name__)


def parse_formdata_array(request, field_name, as_int=False):
    """
    Parse array field from both JSON and FormData
    - JSON: data is dict with lists
    - FormData: data is QueryDict with getlist()
    """
    # Check if data is dict (JSON) or QueryDict (FormData)
    if isinstance(request.data, dict):
        # JSON request
        values = request.data.get(field_name, [])
        if not isinstance(values, list):
            values = [values] if values else []
    else:
        # FormData request
        values = request.data.getlist(field_name)
    
    if not values:
        logger.warning(f"⚠️ {field_name}: empty or not found")
        return []
    
    logger.info(f"✅ {field_name}: {values}")
    
    try:
        if as_int:
            return [int(v) for v in values if v and str(v).strip()]
        return [str(v).strip() for v in values if v and str(v).strip()]
    except (ValueError, TypeError) as e:
        logger.error(f"❌ {field_name} parse error: {e}")
        return []


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project_v2(request):
    """
    Create a new project - Clean implementation
    Endpoint: POST /api/projects/create-new/
    """
    logger.info("=" * 80)
    logger.info("📝 NEW PROJECT CREATION REQUEST")
    logger.info("=" * 80)
    
    # Get teacher
    try:
        teacher = Teacher.objects.get(user=request.user)
        logger.info(f"👤 Teacher: {teacher.full_name}")
    except Teacher.DoesNotExist:
        logger.error("❌ Teacher not found")
        return Response({
            'error': 'المعلم غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Parse FormData arrays
        section_ids = parse_formdata_array(request, 'section_ids', as_int=True)
        logger.info(f"🔍 Parsed section_ids: {section_ids} (type: {type(section_ids)}, length: {len(section_ids)})")
        
        allowed_file_types = parse_formdata_array(request, 'allowed_file_types')
        external_links = parse_formdata_array(request, 'external_links')
        
        # Build data dictionary
        data = {
            'title': request.data.get('title'),
            'subject': request.data.get('subject'),
            'description': request.data.get('description', ''),
            'grade_id': request.data.get('grade_id'),
            'section_ids': section_ids,
            'instructions': request.data.get('instructions', ''),
            'requirements': request.data.get('requirements', ''),
            'tips': request.data.get('tips', ''),
            'allowed_file_types': allowed_file_types,
            'max_file_size': request.data.get('max_file_size_mb', request.data.get('max_file_size', 10)),
            'max_grade': request.data.get('max_grade', 20),
            'start_date': request.data.get('start_date'),
            'deadline': request.data.get('due_date', request.data.get('deadline')),
            'allow_late_submission': str(request.data.get('allow_late_submission', False)).lower() == 'true',
            'send_reminder': str(request.data.get('send_reminder', True)).lower() in ['true', '1', 'yes'],
            'ai_check_plagiarism': str(request.data.get('ai_check_plagiarism', False)).lower() == 'true',
            'external_links': external_links,
        }
        
        # Log data summary
        logger.info(f"📋 Data summary:")
        logger.info(f"  - Title: {data['title']}")
        logger.info(f"  - Sections: {section_ids}")
        logger.info(f"  - File types: {allowed_file_types}")
        logger.info(f"  - Links: {external_links}")
        
        # Validate with serializer
        serializer = ProjectCreateSerializer(data=data)
        if not serializer.is_valid():
            logger.error(f"❌ Validation failed: {serializer.errors}")
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        logger.info("✅ Validation passed")
        
        # Create project
        project = Project.objects.create(
            teacher=teacher,
            title=validated_data['title'],
            subject=validated_data['subject'],
            description=validated_data.get('description', ''),
            start_date=validated_data['start_date'],
            deadline=validated_data['deadline'],
            max_file_size=validated_data['max_file_size'],
            allowed_file_types=validated_data['allowed_file_types'],
            max_grade=validated_data['max_grade'],
            allow_late_submission=validated_data['allow_late_submission'],
            send_reminder=validated_data['send_reminder'],
            ai_check_plagiarism=validated_data['ai_check_plagiarism'],
            instructions=validated_data.get('instructions', ''),
            requirements=validated_data.get('requirements', ''),
            tips=validated_data.get('tips', ''),
        )
        
        logger.info(f"✅ Project created: ID={project.id}")
        
        # Add sections (with telegram_group relation for notifications)
        logger.info(f"🔍 About to add sections. IDs from validated_data: {validated_data['section_ids']}")
        
        sections = Section.objects.filter(
            id__in=validated_data['section_ids']
        ).select_related('telegram_group', 'grade')
        
        logger.info(f"🔍 Sections fetched from DB: {list(sections.values_list('id', 'section_name'))}")
        logger.info(f"🔍 Sections count: {sections.count()}")
        
        project.sections.set(sections)
        
        # Verify what was actually saved
        saved_sections = project.sections.all()
        logger.info(f"✅ Added {sections.count()} sections")
        logger.info(f"✅ Verified: Project now has {saved_sections.count()} sections: {list(saved_sections.values_list('id', 'section_name'))}")
        
        # Handle files
        files_created = 0
        
        # Video
        if 'video' in request.FILES:
            video_file = request.FILES['video']
            ProjectFile.objects.create(
                project=project,
                file_type='video',
                file_path=f'projects/{project.id}/{video_file.name}',
                file_name=video_file.name,
                file_size=video_file.size
            )
            files_created += 1
        
        # PDFs
        for pdf in request.FILES.getlist('pdfs'):
            ProjectFile.objects.create(
                project=project,
                file_type='pdf',
                file_path=f'projects/{project.id}/{pdf.name}',
                file_name=pdf.name,
                file_size=pdf.size
            )
            files_created += 1
        
        # Docs
        for doc in request.FILES.getlist('docs'):
            ProjectFile.objects.create(
                project=project,
                file_type='doc',
                file_path=f'projects/{project.id}/{doc.name}',
                file_name=doc.name,
                file_size=doc.size
            )
            files_created += 1
        
        # External links
        external_links_list = validated_data.get('external_links', [])
        logger.info(f"🔗 External links received: {external_links_list}")
        logger.info(f"🔗 External links count: {len(external_links_list)}")
        
        for link in external_links_list:
            if link and link.strip():
                logger.info(f"💾 Saving link: {link}")
                file_obj = ProjectFile.objects.create(
                    project=project,
                    file_type='link',
                    file_path=link,
                    external_link=link,  # ✅ حفظ في external_link أيضاً
                    file_name=link
                )
                files_created += 1
                logger.info(f"✅ Link saved successfully with ID: {file_obj.id}")
        
        logger.info(f"✅ Added {files_created} files/links total")
        
        # Send Telegram notifications (optional based on user choice)
        telegram_results = {'success': [], 'failed': [], 'total': 0, 'sent': False}
        send_telegram_now = validated_data.get('send_telegram_now', False)
        
        if send_telegram_now and project.send_reminder:
            logger.info("📱 Sending Telegram notifications...")
            try:
                from .telegram_helper import TelegramProjectNotifier
                
                notifier = TelegramProjectNotifier()
                result = notifier.send_project_notification(project, send_files=True, pin_message=True)
                
                if result:
                    telegram_results = {
                        'success': result.get('success', []),
                        'failed': result.get('failed', []),
                        'total': result.get('total', 0),
                        'sent': True
                    }
                    
                    for success_item in telegram_results['success']:
                        logger.info(f"✅ Telegram sent to {success_item.get('section')}")
                    
                    for failed_item in telegram_results['failed']:
                        logger.warning(f"⚠️ Telegram failed for {failed_item.get('section')}: {failed_item.get('error')}")
                    
                    project.telegram_sent = len(telegram_results['success']) > 0
                    project.save()
                else:
                    logger.warning("⚠️ Telegram notification returned no results")
                    
            except Exception as e:
                logger.error(f"❌ Telegram notification error: {str(e)}")
                telegram_results['failed'].append({
                    'error': str(e)
                })
        else:
            logger.info("⏭️ Skipping Telegram notifications (send_telegram_now=False or send_reminder=False)")
        
        logger.info("=" * 80)
        logger.info("✅ PROJECT CREATED SUCCESSFULLY")
        logger.info("=" * 80)
        
        # Reload project with all relations for complete serializer data
        project_complete = Project.objects.prefetch_related(
            'sections__grade',
            'sections__telegram_group'
        ).get(id=project.id)
        
        # Use full serializer to get grade_display and all fields
        from .serializers import ProjectSerializer
        project_serializer = ProjectSerializer(project_complete)
        
        # Return response with complete project data
        return Response({
            'success': True,
            'message': 'تم إنشاء المشروع بنجاح',
            'project': project_serializer.data,  # Complete data with grade_display
            'telegram': telegram_results  # Separated for clarity
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return Response({
            'error': 'حدث خطأ غير متوقع',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
