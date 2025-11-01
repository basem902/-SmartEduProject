"""
Test adding a student directly to database
اختبار إضافة طالب مباشرة إلى قاعدة البيانات
"""

import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration, Section, SchoolGrade, Teacher
from apps.accounts.models import User

def test_add_student():
    """اختبار إضافة طالب"""
    
    print("=" * 60)
    print("🔍 اختبار إضافة طالب إلى Database")
    print("=" * 60)
    
    # Get teacher
    try:
        teacher_user = User.objects.get(username='basem902')
        teacher = Teacher.objects.get(user=teacher_user)
        print(f"✅ وجدت المعلم: {teacher.user.username}")
    except:
        print("❌ لم أجد المعلم basem902")
        return
    
    # Get first grade
    try:
        grade = SchoolGrade.objects.filter(teacher=teacher, is_active=True).first()
        if not grade:
            print("❌ لا توجد صفوف نشطة للمعلم")
            return
        print(f"✅ وجدت الصف: {grade.display_name}")
    except Exception as e:
        print(f"❌ خطأ في الحصول على الصف: {e}")
        return
    
    # Get first section
    try:
        section = Section.objects.filter(grade=grade).first()
        if not section:
            print("❌ لا توجد شعب في هذا الصف")
            print("\n💡 يجب إنشاء شعبة أولاً!")
            print("   اذهب إلى: إعدادات الصفوف → أضف شعبة")
            return
        print(f"✅ وجدت الشعبة: {section.section_name}")
    except Exception as e:
        print(f"❌ خطأ في الحصول على الشعبة: {e}")
        return
    
    # Try to add student
    try:
        from apps.sections.utils import ArabicNameNormalizer
        
        full_name = "اختبار طالب تجريبي"
        normalized_name = ArabicNameNormalizer.normalize(full_name)
        
        student = StudentRegistration.objects.create(
            full_name=full_name,
            normalized_name=normalized_name,
            teacher=teacher,
            school_name=teacher.school_name or 'مدرستي',
            grade=grade,
            section=section,
            telegram_invite_link='',
            registration_ip='127.0.0.1',
            user_agent='Test Script'
        )
        
        print(f"\n✅ تم إضافة الطالب بنجاح!")
        print(f"   ID: {student.id}")
        print(f"   الاسم: {student.full_name}")
        print(f"   الشعبة: {student.section.section_name}")
        
        # Clean up
        confirm = input("\n⚠️  هل تريد حذف الطالب التجريبي؟ (yes/no): ")
        if confirm.lower() == 'yes':
            student.delete()
            print("✅ تم حذف الطالب التجريبي")
        
    except Exception as e:
        print(f"\n❌ فشل إضافة الطالب!")
        print(f"   الخطأ: {e}")
        
        import traceback
        print(f"\n📋 التفاصيل الكاملة:")
        print(traceback.format_exc())

if __name__ == '__main__':
    test_add_student()
