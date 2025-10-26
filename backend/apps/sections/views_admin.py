"""
Admin Views - إدارة قاعدة البيانات
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from apps.sections.models import (
    SchoolGrade, Section, SectionLink, TelegramGroup,
    AIGeneratedContent, TeacherJoinLink, StudentRegistration
)
from apps.projects.models import Project, ProjectFile


@api_view(['POST'])
@permission_classes([IsAdminUser])
def wipe_all_data(request):
    """
    🗑️ حذف جميع البيانات من قاعدة البيانات
    
    POST /api/admin/wipe-all-data/
    
    ⚠️ عملية خطرة - تحذف جميع البيانات ماعدا المعلمين
    """
    
    total_deleted = 0
    deleted_details = {}
    
    try:
        # ==================== Projects App ====================
        
        # حذف ملفات المشاريع
        result = ProjectFile.objects.all().delete()
        deleted_details['project_files'] = result[0]
        total_deleted += result[0]
        
        # حذف المشاريع
        result = Project.objects.all().delete()
        deleted_details['projects'] = result[0]
        total_deleted += result[0]
        
        # ==================== Sections App ====================
        
        # حذف تسجيلات الطلاب
        result = StudentRegistration.objects.all().delete()
        deleted_details['student_registrations'] = result[0]
        total_deleted += result[0]
        
        # حذف روابط المعلمين
        result = TeacherJoinLink.objects.all().delete()
        deleted_details['teacher_join_links'] = result[0]
        total_deleted += result[0]
        
        # حذف روابط الشُعب
        result = SectionLink.objects.all().delete()
        deleted_details['section_links'] = result[0]
        total_deleted += result[0]
        
        # حذف قروبات Telegram
        result = TelegramGroup.objects.all().delete()
        deleted_details['telegram_groups'] = result[0]
        total_deleted += result[0]
        
        # حذف محتوى AI
        result = AIGeneratedContent.objects.all().delete()
        deleted_details['ai_content'] = result[0]
        total_deleted += result[0]
        
        # حذف الشُعب
        result = Section.objects.all().delete()
        deleted_details['sections'] = result[0]
        total_deleted += result[0]
        
        # حذف الصفوف
        result = SchoolGrade.objects.all().delete()
        deleted_details['school_grades'] = result[0]
        total_deleted += result[0]
        
        return Response({
            'success': True,
            'message': f'تم حذف {total_deleted} سجل بنجاح',
            'total_deleted': total_deleted,
            'details': deleted_details
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'حدث خطأ: {str(e)}',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_database_stats(request):
    """
    📊 إحصائيات قاعدة البيانات
    
    GET /api/admin/database-stats/
    """
    
    try:
        stats = {
            'projects': {
                'projects': Project.objects.count(),
                'project_files': ProjectFile.objects.count(),
            },
            'sections': {
                'school_grades': SchoolGrade.objects.count(),
                'sections': Section.objects.count(),
                'section_links': SectionLink.objects.count(),
                'telegram_groups': TelegramGroup.objects.count(),
                'ai_content': AIGeneratedContent.objects.count(),
                'teacher_join_links': TeacherJoinLink.objects.count(),
                'student_registrations': StudentRegistration.objects.count(),
            },
            'total_records': (
                Project.objects.count() +
                ProjectFile.objects.count() +
                SchoolGrade.objects.count() +
                Section.objects.count() +
                SectionLink.objects.count() +
                TelegramGroup.objects.count() +
                AIGeneratedContent.objects.count() +
                TeacherJoinLink.objects.count() +
                StudentRegistration.objects.count()
            )
        }
        
        return Response({
            'success': True,
            'stats': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'حدث خطأ: {str(e)}',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
