"""
Views for Admin Panel APIs
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import require_superuser
from .utils import (
    get_all_tables, get_table_count, get_table_data,
    truncate_table, reset_sequence, get_database_statistics,
    delete_row
)
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    تسجيل دخول المدير
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'يرجى إدخال اسم المستخدم وكلمة المرور'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if superuser
        if not user.is_superuser:
            return Response({
                'error': 'هذا الحساب لا يملك صلاحيات الإدارة'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"Admin login successful: {username}")
        
        return Response({
            'message': 'تم تسجيل الدخول بنجاح',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء تسجيل الدخول',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@require_superuser
def list_tables(request):
    """
    الحصول على قائمة بجميع الجداول مع عدد السجلات
    """
    try:
        tables = get_all_tables()
        tables_info = []
        
        for table in tables:
            count = get_table_count(table)
            tables_info.append({
                'name': table,
                'count': count
            })
        
        return Response({
            'tables': tables_info,
            'total': len(tables_info)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"List tables error: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء جلب قائمة الجداول',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@require_superuser
def get_table_data_view(request, table_name):
    """
    الحصول على بيانات جدول معين
    """
    try:
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        
        data = get_table_data(table_name, limit, offset)
        total_count = get_table_count(table_name)
        
        return Response({
            'table_name': table_name,
            'columns': data['columns'],
            'data': data['data'],
            'count': len(data['data']),
            'total': total_count,
            'limit': limit,
            'offset': offset
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get table data error for {table_name}: {str(e)}")
        return Response({
            'error': f'حدث خطأ أثناء جلب بيانات الجدول {table_name}',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@require_superuser
def truncate_table_view(request, table_name):
    """
    حذف جميع بيانات جدول معين
    """
    try:
        # Confirmation check
        confirm = request.data.get('confirm')
        if confirm != 'DELETE':
            return Response({
                'error': 'يجب تأكيد الحذف عن طريق إرسال confirm: DELETE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get count before delete
        count = get_table_count(table_name)
        
        # Truncate
        truncate_table(table_name)
        
        logger.warning(f"Table {table_name} truncated by {request.user.username}. Deleted {count} rows.")
        
        return Response({
            'message': f'تم حذف جميع البيانات من جدول {table_name}',
            'deleted_count': count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Truncate table error for {table_name}: {str(e)}")
        return Response({
            'error': f'حدث خطأ أثناء حذف بيانات الجدول {table_name}',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@require_superuser
def delete_row_view(request, table_name, row_id):
    """
    حذف سجل واحد من جدول معين
    """
    try:
        # معالجة خاصة لجدول teachers
        if table_name == 'teachers':
            from apps.accounts.models import Teacher
            teacher = Teacher.objects.filter(id=row_id).first()
            if teacher:
                # حذف User المرتبط إذا كان موجوداً
                if teacher.user:
                    teacher.user.delete()  # سيحذف Teacher تلقائياً بسبب CASCADE
                else:
                    teacher.delete()
            else:
                return Response({
                    'error': 'السجل غير موجود'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # حذف عادي للجداول الأخرى
            delete_row(table_name, row_id)
        
        logger.info(f"Row {row_id} deleted from {table_name} by {request.user.username}")
        
        return Response({
            'message': f'تم حذف السجل رقم {row_id} من جدول {table_name}',
            'deleted_id': row_id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Delete row error for {table_name}/{row_id}: {str(e)}")
        return Response({
            'error': f'حدث خطأ أثناء حذف السجل',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@require_superuser
def reset_sequence_view(request, table_name):
    """
    تصفير عداد الـ auto-increment لجدول معين
    """
    try:
        success = reset_sequence(table_name)
        
        if success:
            logger.info(f"Sequence reset for {table_name} by {request.user.username}")
            return Response({
                'message': f'تم تصفير العداد للجدول {table_name}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': f'لم يتم العثور على عداد للجدول {table_name}'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Reset sequence error for {table_name}: {str(e)}")
        return Response({
            'error': f'حدث خطأ أثناء تصفير العداد للجدول {table_name}',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@require_superuser
def get_statistics(request):
    """
    الحصول على إحصائيات عامة عن قاعدة البيانات
    """
    try:
        stats = get_database_statistics()
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get statistics error: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء جلب الإحصائيات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@require_superuser
def delete_teacher_sections_data(request, teacher_id):
    """
    حذف بيانات الشُعب والتيليجرام للمعلم مع الاحتفاظ ببيانات المعلم
    """
    try:
        from django.db import connection
        from apps.accounts.models import Teacher
        
        # التحقق من وجود المعلم
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response({
                'error': 'المعلم غير موجود'
            }, status=status.HTTP_404_NOT_FOUND)
        
        deleted_counts = {}
        
        with connection.cursor() as cursor:
            # 1. حذف قروبات تيليجرام المرتبطة بشُعب المعلم
            cursor.execute("""
                DELETE FROM telegram_groups 
                WHERE section_id IN (
                    SELECT s.id FROM sections s
                    JOIN school_grades sg ON s.grade_id = sg.id
                    WHERE sg.teacher_id = %s
                )
            """, [teacher_id])
            deleted_counts['telegram_groups'] = cursor.rowcount
            
            # 2. حذف تسجيلات الطلاب في الشُعب
            cursor.execute("""
                DELETE FROM student_registrations 
                WHERE section_id IN (
                    SELECT s.id FROM sections s
                    JOIN school_grades sg ON s.grade_id = sg.id
                    WHERE sg.teacher_id = %s
                )
            """, [teacher_id])
            deleted_counts['student_registrations'] = cursor.rowcount
            
            # 3. حذف روابط الشُعب
            cursor.execute("""
                DELETE FROM section_links 
                WHERE section_id IN (
                    SELECT s.id FROM sections s
                    JOIN school_grades sg ON s.grade_id = sg.id
                    WHERE sg.teacher_id = %s
                )
            """, [teacher_id])
            deleted_counts['section_links'] = cursor.rowcount
            
            # 4. حذف محتوى AI المرتبط بالمعلم
            cursor.execute("""
                DELETE FROM ai_generated_content 
                WHERE teacher_id = %s
            """, [teacher_id])
            deleted_counts['ai_generated_content'] = cursor.rowcount
            
            # 5. حذف الشُعب
            cursor.execute("""
                DELETE FROM sections 
                WHERE grade_id IN (
                    SELECT id FROM school_grades 
                    WHERE teacher_id = %s
                )
            """, [teacher_id])
            deleted_counts['sections'] = cursor.rowcount
            
            # 6. حذف الصفوف الدراسية
            cursor.execute("""
                DELETE FROM school_grades 
                WHERE teacher_id = %s
            """, [teacher_id])
            deleted_counts['school_grades'] = cursor.rowcount
        
        total_deleted = sum(deleted_counts.values())
        
        logger.warning(f"Sections data deleted for teacher {teacher.full_name} (ID: {teacher_id}) by {request.user.username}. Total: {total_deleted} records")
        
        return Response({
            'message': f'تم حذف بيانات الشُعب للمعلم {teacher.full_name} بنجاح',
            'teacher': {
                'id': teacher.id,
                'name': teacher.full_name,
                'email': teacher.email
            },
            'deleted': deleted_counts,
            'total_deleted': total_deleted
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Delete teacher sections data error: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء حذف البيانات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@require_superuser
def wipe_all_data(request):
    """
    حذف جميع البيانات من القاعدة (عملية خطرة جداً!)
    """
    try:
        # Strong confirmation required
        confirm_text = request.data.get('confirm')
        admin_password = request.data.get('password')
        
        if confirm_text != 'DELETE ALL DATA':
            return Response({
                'error': 'يجب كتابة "DELETE ALL DATA" للتأكيد'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify admin password again
        user = authenticate(username=request.user.username, password=admin_password)
        if not user:
            return Response({
                'error': 'كلمة المرور غير صحيحة'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get all tables
        tables = get_all_tables()
        deleted_counts = {}
        
        for table in tables:
            if table not in ['django_migrations', 'django_content_type', 'auth_permission']:
                count = get_table_count(table)
                truncate_table(table)
                deleted_counts[table] = count
        
        logger.critical(f"ALL DATA WIPED by {request.user.username}. Total deleted: {sum(deleted_counts.values())}")
        
        return Response({
            'message': 'تم حذف جميع البيانات من القاعدة',
            'deleted_tables': deleted_counts,
            'total_deleted': sum(deleted_counts.values())
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Wipe all data error: {str(e)}")
        return Response({
            'error': 'حدث خطأ أثناء حذف البيانات',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
