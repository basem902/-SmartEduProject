"""
Utility functions for Admin Panel
"""
from django.db import connection
from django.apps import apps


def get_all_tables():
    """
    الحصول على قائمة بجميع جداول قاعدة البيانات
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
    return tables


def get_table_count(table_name):
    """
    الحصول على عدد السجلات في جدول معين
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
            count = cursor.fetchone()[0]
        return count
    except Exception:
        return 0


def get_table_columns(table_name):
    """
    الحصول على أسماء الأعمدة في جدول معين
    """
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        columns = [{'name': row[0], 'type': row[1]} for row in cursor.fetchall()]
    return columns


def get_table_data(table_name, limit=100, offset=0):
    """
    الحصول على بيانات جدول معين
    """
    with connection.cursor() as cursor:
        # Get columns
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        # Get data
        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT {limit} OFFSET {offset};')
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
    
    return {'columns': columns, 'data': data}


def truncate_table(table_name):
    """
    حذف جميع البيانات من جدول معين
    """
    with connection.cursor() as cursor:
        cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')
    return True


def reset_sequence(table_name):
    """
    تصفير عداد الـ auto-increment لجدول معين
    """
    with connection.cursor() as cursor:
        # Find the sequence name
        cursor.execute(f"""
            SELECT pg_get_serial_sequence('"{table_name}"', 'id');
        """)
        sequence = cursor.fetchone()
        
        if sequence and sequence[0]:
            cursor.execute(f"ALTER SEQUENCE {sequence[0]} RESTART WITH 1;")
            return True
    return False


def delete_row(table_name, row_id):
    """
    حذف سجل واحد من جدول معين
    """
    with connection.cursor() as cursor:
        cursor.execute(f'DELETE FROM "{table_name}" WHERE id = %s;', [row_id])
    return True


def get_database_statistics():
    """
    الحصول على إحصائيات عامة عن قاعدة البيانات
    """
    tables = get_all_tables()
    stats = {
        'total_tables': len(tables),
        'tables': []
    }
    
    for table in tables:
        count = get_table_count(table)
        stats['tables'].append({
            'name': table,
            'count': count
        })
    
    return stats
