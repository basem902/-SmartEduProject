"""
🗑️ حذف جميع البيانات من جميع الجداول
(ماعدا المعلمين والإعدادات)
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import (
    SchoolGrade, Section, SectionLink, TelegramGroup,
    AIGeneratedContent, TeacherJoinLink, StudentRegistration
)
from apps.projects.models import Project, ProjectFile

print("=" * 70)
print("🗑️  حذف جميع البيانات من جميع الجداول")
print("=" * 70)

total_deleted = 0

# ==================== Projects App ====================
print("\n📚 حذف بيانات المشاريع...")

try:
    deleted = ProjectFile.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} ملف مشروع")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف ملفات المشاريع: {e}")

try:
    deleted = Project.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} مشروع")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف المشاريع: {e}")

# ==================== Sections App ====================
print("\n📋 حذف بيانات الصفوف والشُعب...")

try:
    deleted = StudentRegistration.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} تسجيل طالب")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف تسجيلات الطلاب: {e}")

try:
    deleted = TeacherJoinLink.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} رابط انضمام معلم")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف روابط المعلمين: {e}")

try:
    deleted = SectionLink.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} رابط شعبة")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف روابط الشُعب: {e}")

try:
    deleted = TelegramGroup.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} قروب Telegram")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف قروبات Telegram: {e}")

try:
    deleted = AIGeneratedContent.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} محتوى AI")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف محتوى AI: {e}")

try:
    deleted = Section.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} شعبة")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف الشُعب: {e}")

try:
    deleted = SchoolGrade.objects.all().delete()
    print(f"  ✅ تم حذف {deleted[0]} صف")
    total_deleted += deleted[0]
except Exception as e:
    print(f"  ⚠️ خطأ في حذف الصفوف: {e}")

# ==================== Summary ====================
print("\n" + "=" * 70)
print(f"✅ تم حذف {total_deleted} سجل بنجاح!")
print("=" * 70)
print("\n📝 ملاحظة: لم يتم حذف بيانات المعلمين والإعدادات")
print("\n🚀 الآن يمكنك تشغيل:")
print("  python manage.py makemigrations sections")
print("  python manage.py migrate")
