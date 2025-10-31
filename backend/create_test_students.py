"""
🧪 إنشاء طلاب تجريبيين في قاعدة البيانات وقروبات التليجرام
"""
import os
import sys
import django
from pathlib import Path

# إعداد Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.sections.models import (
    SchoolGrade, Section, TelegramGroup, StudentRegistration
)
from apps.accounts.models import User, Teacher
from apps.projects.models import Project


def create_test_data():
    """إنشاء بيانات تجريبية كاملة"""
    
    print("=" * 60)
    print("🧪 إنشاء بيانات تجريبية")
    print("=" * 60)
    print()
    
    # 1. المعلم
    print("👨‍🏫 إنشاء معلم تجريبي...")
    teacher_user, created = User.objects.get_or_create(
        username='test_teacher',
        defaults={
            'email': 'teacher@smartedu.com',
            'first_name': 'أحمد',
            'last_name': 'المعلم',
            'role': 'teacher',
            'is_active': True
        }
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
    
    teacher, created = Teacher.objects.get_or_create(
        user=teacher_user,
        defaults={
            'phone': '+966500000001',
            'subject': 'الحاسب الآلي'
        }
    )
    print(f"   ✅ المعلم: {teacher.user.get_full_name()}")
    print(f"   📧 البريد: {teacher.user.email}")
    print(f"   🔑 كلمة المرور: teacher123")
    print()
    
    # 2. الصفوف الدراسية
    print("📚 إنشاء الصفوف الدراسية...")
    grades_data = [
        {'level': 'high', 'grade_number': 1, 'school': 'مدرسة النجاح الثانوية', 'subject': 'المهارات الرقمية'},
        {'level': 'high', 'grade_number': 2, 'school': 'مدرسة الأمل الثانوية', 'subject': 'المهارات الرقمية'},
        {'level': 'high', 'grade_number': 3, 'school': 'مدرسة التميز الثانوية', 'subject': 'المهارات الرقمية'},
    ]
    
    grades = []
    for grade_data in grades_data:
        grade, created = SchoolGrade.objects.get_or_create(
            teacher=teacher,
            level=grade_data['level'],
            grade_number=grade_data['grade_number'],
            subject=grade_data['subject'],
            defaults={
                'school_name': grade_data['school'],
                'is_active': True
            }
        )
        grades.append(grade)
        print(f"   {'✅' if created else 'ℹ️'} {grade.display_name}")
    print()
    
    # 3. الشُعب
    print("📖 إنشاء الشُعب...")
    sections_data = [
        {'grade': grades[0], 'name': '1/1'},
        {'grade': grades[0], 'name': '1/2'},
        {'grade': grades[1], 'name': '2/1'},
        {'grade': grades[2], 'name': '3/1'},
    ]
    
    sections = []
    for sec_data in sections_data:
        section, created = Section.objects.get_or_create(
            grade=sec_data['grade'],
            section_name=sec_data['name'],
            defaults={
                'is_active': True
            }
        )
        sections.append(section)
        print(f"   {'✅' if created else 'ℹ️'} {sec_data['grade'].display_name} - شعبة {sec_data['name']}")
    print()
    
    # 5. قروبات التليجرام
    print("📱 إنشاء قروبات تليجرام...")
    telegram_groups = []
    
    # ملاحظة: استبدل هذه بمعرفات قروباتك الحقيقية
    groups_data = [
        {
            'section': sections[0],
            'name': 'قروب الأول الثانوي 1/1',
            'chat_id': '-1001234567890',  # استبدل بمعرف قروبك
            'invite_link': 'https://t.me/+test_group_1'
        },
        {
            'section': sections[1],
            'name': 'قروب الأول الثانوي 1/2',
            'chat_id': '-1001234567891',
            'invite_link': 'https://t.me/+test_group_2'
        },
        {
            'section': sections[2],
            'name': 'قروب الثاني الثانوي 2/1',
            'chat_id': '-1001234567892',
            'invite_link': 'https://t.me/+test_group_3'
        },
        {
            'section': sections[3],
            'name': 'قروب الثالث الثانوي 3/1',
            'chat_id': '-1001234567893',
            'invite_link': 'https://t.me/+test_group_4'
        },
    ]
    
    for group_data in groups_data:
        group, created = TelegramGroup.objects.get_or_create(
            section=group_data['section'],
            defaults={
                'group_name': group_data['name'],
                'telegram_chat_id': group_data['chat_id'],
                'invite_link': group_data['invite_link'],
                'is_active': True
            }
        )
        telegram_groups.append(group)
        print(f"   {'✅' if created else 'ℹ️'} {group_data['name']}")
        print(f"      Chat ID: {group_data['chat_id']}")
    print()
    
    # 6. الطلاب التجريبيين
    print("👥 إنشاء طلاب تجريبيين...")
    
    students_data = [
        # شعبة 1/1
        {
            'name': 'محمد أحمد علي حسن',
            'section': sections[0],
            'telegram_group': telegram_groups[0],
            'telegram_id': 123456789,
            'telegram_username': 'mohammed_test'
        },
        {
            'name': 'فاطمة عبدالله سعيد محمد',
            'section': sections[0],
            'telegram_group': telegram_groups[0],
            'telegram_id': 123456790,
            'telegram_username': 'fatima_test'
        },
        {
            'name': 'عبدالرحمن خالد يوسف إبراهيم',
            'section': sections[0],
            'telegram_group': telegram_groups[0],
            'telegram_id': 123456791,
            'telegram_username': 'abdulrahman_test'
        },
        
        # شعبة 1/2
        {
            'name': 'سارة علي محمد حسن',
            'section': sections[1],
            'telegram_group': telegram_groups[1],
            'telegram_id': 123456792,
            'telegram_username': 'sara_test'
        },
        {
            'name': 'عبدالله خالد أحمد يوسف',
            'section': sections[1],
            'telegram_group': telegram_groups[1],
            'telegram_id': 123456793,
            'telegram_username': 'abdullah_test'
        },
        
        # شعبة 2/1
        {
            'name': 'نور الدين عبدالرحمن علي محمد',
            'section': sections[2],
            'telegram_group': telegram_groups[2],
            'telegram_id': 123456794,
            'telegram_username': 'nour_test'
        },
        {
            'name': 'مريم يوسف إبراهيم حسن',
            'section': sections[2],
            'telegram_group': telegram_groups[2],
            'telegram_id': 123456795,
            'telegram_username': 'mariam_test'
        },
        
        # شعبة 3/1
        {
            'name': 'خالد محمد عبدالله سعيد',
            'section': sections[3],
            'telegram_group': telegram_groups[3],
            'telegram_id': 123456796,
            'telegram_username': 'khalid_test'
        },
        {
            'name': 'هدى أحمد علي محمد',
            'section': sections[3],
            'telegram_group': telegram_groups[3],
            'telegram_id': 123456797,
            'telegram_username': 'huda_test'
        },
        {
            'name': 'عمر سعيد يوسف حسن',
            'section': sections[3],
            'telegram_group': telegram_groups[3],
            'telegram_id': 123456798,
            'telegram_username': 'omar_test'
        },
    ]
    
    created_students = []
    from apps.projects.utils import normalize_arabic_name
    
    for student_data in students_data:
        student, created = StudentRegistration.objects.get_or_create(
            teacher=teacher,
            grade=student_data['section'].grade,
            section=student_data['section'],
            normalized_name=normalize_arabic_name(student_data['name']),
            defaults={
                'full_name': student_data['name'],
                'telegram_user_id': student_data['telegram_id'],
                'telegram_username': student_data['telegram_username'],
                'telegram_group': student_data['telegram_group'],
                'school_name': student_data['section'].grade.school_name,
                'joined_telegram': True,
                'joined_at': timezone.now()
            }
        )
        created_students.append(student)
        status = '✅ جديد' if created else 'ℹ️ موجود'
        print(f"   {status} {student.full_name}")
        print(f"      الشعبة: {student.section.section_name}")
        print(f"      Telegram: @{student.telegram_username} ({student.telegram_user_id})")
    print()
    
    # 7. مشروع تجريبي
    print("📁 إنشاء مشروع تجريبي...")
    project, created = Project.objects.get_or_create(
        title="مشروع اختبار النظام الكامل",
        teacher=teacher,
        defaults={
            'description': 'مشروع لاختبار نظام الذكاء الاصطناعي والتحقق من التليجرام',
            'deadline': timezone.now() + timedelta(days=7),
            'allowed_file_types': ['pdf', 'video', 'image', 'document', 'audio'],
            'max_file_size': 52428800,  # 50 MB
            'max_attempts': 3,
            'ai_validation_enabled': True,
            'file_constraints': {
                'video': {
                    'min_duration': 15,
                    'max_duration': 300,
                    'min_quality': 480
                },
                'pdf': {
                    'min_pages': 3,
                    'max_pages': 20,
                    'min_words': 500
                }
            }
        }
    )
    
    # ربط المشروع بجميع الشُعب
    for section in sections:
        project.sections.add(section)
    
    print(f"   {'✅ تم الإنشاء' if created else 'ℹ️ موجود مسبقاً'}")
    print(f"   العنوان: {project.title}")
    print(f"   الموعد النهائي: {project.deadline.strftime('%Y-%m-%d %H:%M')}")
    print(f"   الشُعب المرتبطة: {project.sections.count()}")
    print()
    
    # ملخص
    print("=" * 60)
    print("✅ انتهى إنشاء البيانات التجريبية!")
    print("=" * 60)
    print()
    print("📊 الملخص:")
    print(f"   📚 صفوف دراسية: {SchoolGrade.objects.count()}")
    print(f"   📖 شُعب: {Section.objects.count()}")
    print(f"   👨‍🏫 معلمين: {Teacher.objects.count()}")
    print(f"   📱 قروبات تليجرام: {TelegramGroup.objects.count()}")
    print(f"   👥 طلاب: {StudentRegistration.objects.count()}")
    print(f"   📁 مشاريع: {Project.objects.count()}")
    print()
    
    print("💡 معلومات مهمة:")
    print(f"   📧 بريد المعلم: teacher@smartedu.com")
    print(f"   🔑 كلمة المرور: teacher123")
    print(f"   🎯 معرف المشروع: {project.id}")
    print()
    
    print("🧪 طلاب جاهزون للاختبار:")
    for student in created_students[:3]:
        print(f"   • {student.full_name}")
        print(f"     الشعبة: {student.section.section_name}")
        print(f"     Telegram ID: {student.telegram_user_id}")
    print()
    
    print("⚠️ ملاحظة مهمة:")
    print("   معرفات قروبات التليجرام (-1001234567890) هي أمثلة فقط!")
    print("   استبدلها بمعرفات قروباتك الحقيقية في السكريبت.")
    print()
    
    return {
        'grades': grades,
        'sections': sections,
        'teacher': teacher,
        'telegram_groups': telegram_groups,
        'students': created_students,
        'project': project
    }


if __name__ == '__main__':
    try:
        result = create_test_data()
        print("🎉 نجح إنشاء البيانات التجريبية!")
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
