"""
Test endpoint to save project data to JSON file
For debugging and inspection purposes
"""
import json
import logging
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os

logger = logging.getLogger(__name__)


def parse_formdata_array(request, field_name, as_int=False):
    """Helper to parse FormData arrays from Django request"""
    values = request.data.getlist(field_name)
    if not values:
        return []
    if as_int:
        return [int(v) for v in values if v]
    return [str(v).strip() for v in values if v]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_project_create(request):
    """
    Test endpoint - saves project data to JSON file
    Does NOT save to database
    """
    logger.info("=" * 80)
    logger.info("🧪 TEST ENDPOINT CALLED - Saving to JSON file")
    logger.info("=" * 80)
    
    try:
        # Parse all data
        data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'user': request.user.username,
                'teacher_id': request.user.id,
                'content_type': request.content_type
            },
            'basic_info': {
                'title': request.data.get('title', ''),
                'subject': request.data.get('subject', ''),
                'description': request.data.get('description', '')
            },
            'target': {
                'grade_id': request.data.get('grade_id'),
                'section_ids': parse_formdata_array(request, 'section_ids', as_int=True)
            },
            'instructions': {
                'instructions': request.data.get('instructions', ''),
                'requirements': request.data.get('requirements', ''),
                'tips': request.data.get('tips', '')
            },
            'settings': {
                'allowed_file_types': parse_formdata_array(request, 'allowed_file_types'),
                'max_file_size': request.data.get('max_file_size', 10),
                'max_grade': request.data.get('max_grade', 20),
                'start_date': request.data.get('start_date'),
                'deadline': request.data.get('deadline'),
                'allow_late_submission': request.data.get('allow_late_submission', 'false').lower() == 'true',
                'send_reminder': request.data.get('send_reminder', 'false').lower() == 'true',
                'ai_check_plagiarism': request.data.get('ai_check_plagiarism', 'false').lower() == 'true'
            },
            'telegram': {
                'send_telegram_now': request.data.get('send_telegram_now', 'false').lower() == 'true'
            },
            'files': {
                'video': str(request.FILES.get('video')) if 'video' in request.FILES else None,
                'video_link': request.data.get('video_link', ''),
                'pdfs': [str(f) for f in request.FILES.getlist('pdfs')],
                'docs': [str(f) for f in request.FILES.getlist('docs')],
                'external_links': parse_formdata_array(request, 'external_links')
            },
            'raw_formdata': {}
        }
        
        # Capture all FormData entries
        for key in request.data.keys():
            values = request.data.getlist(key)
            if len(values) == 1:
                data['raw_formdata'][key] = values[0]
            else:
                data['raw_formdata'][key] = values
        
        # Log to console
        logger.info("📦 PARSED DATA:")
        logger.info(f"  Title: {data['basic_info']['title']}")
        logger.info(f"  Subject: {data['basic_info']['subject']}")
        logger.info(f"  Grade ID: {data['target']['grade_id']}")
        logger.info(f"  Section IDs: {data['target']['section_ids']}")
        logger.info(f"  Allowed File Types: {data['settings']['allowed_file_types']}")
        logger.info(f"  External Links: {data['files']['external_links']}")
        logger.info(f"  Video: {data['files']['video']}")
        logger.info(f"  PDFs: {data['files']['pdfs']}")
        logger.info(f"  Docs: {data['files']['docs']}")
        
        # Save to JSON file
        output_dir = os.path.join(settings.BASE_DIR, 'test_output')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'project_test_{timestamp}.json'
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Data saved to: {filepath}")
        logger.info("=" * 80)
        
        return Response({
            'success': True,
            'message': 'بيانات الاختبار تم حفظها في ملف JSON',
            'file_path': filepath,
            'filename': filename,
            'data_summary': {
                'title': data['basic_info']['title'],
                'sections_count': len(data['target']['section_ids']),
                'file_types': data['settings']['allowed_file_types'],
                'external_links_count': len(data['files']['external_links']),
                'has_video': bool(data['files']['video']),
                'pdfs_count': len(data['files']['pdfs']),
                'docs_count': len(data['files']['docs'])
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error in test endpoint: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
