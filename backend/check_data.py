"""
🔍 فحص البيانات التجريبية
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.projects.models import Project
from apps.sections.models import StudentRegistration

print("=" * 60)
print("🔍 فحص البيانات")
print("=" * 60)
print()

# 1. المشاريع
print("📁 المشاريع:")
projects = Project.objects.all()
for p in projects:
    print(f"   ID: {p.id} - {p.title}")
    print(f"      الشُعب المرتبطة: {p.sections.count()}")
    if p.sections.exists():
        for s in p.sections.all():
            print(f"         • {s.section_name} (ID: {s.id})")
print()

# 2. الطلاب
print("👥 الطلاب:")
students = StudentRegistration.objects.all()
print(f"   عدد الطلاب: {students.count()}")
for s in students[:5]:
    print(f"   • {s.full_name}")
    print(f"     الشعبة: {s.section.section_name} (ID: {s.section.id})")
    print(f"     Normalized: {s.normalized_name}")
print()

# 3. التحقق من المشروع 5
print("🎯 المشروع 5:")
try:
    project = Project.objects.get(id=5)
    print(f"   العنوان: {project.title}")
    print(f"   الشُعب: {project.sections.count()}")
    
    # البحث عن طالب
    print()
    print("🔍 البحث عن طالب:")
    test_name = "محمد أحمد علي حسن"
    
    # تطبيع الاسم
    import re
    def normalize_arabic_name(name):
        name = ' '.join(name.split())
        name = re.sub('[إأآا]', 'ا', name)
        name = re.sub('ى', 'ي', name)
        name = re.sub('ة', 'ه', name)
        return name.strip().lower()
    
    normalized = normalize_arabic_name(test_name)
    print(f"   الاسم: {test_name}")
    print(f"   المُطبّع: {normalized}")
    
    # البحث
    students = StudentRegistration.objects.filter(
        section__in=project.sections.all(),
        normalized_name=normalized
    )
    
    print(f"   النتائج: {students.count()}")
    if students.exists():
        for s in students:
            print(f"      ✅ وُجد: {s.full_name} (الشعبة: {s.section.section_name})")
    else:
        print(f"      ❌ لم يُوجد!")
        
        # البحث في جميع الشُعب
        print()
        print("   🔍 البحث في جميع الشُعب:")
        all_students = StudentRegistration.objects.filter(
            normalized_name=normalized
        )
        if all_students.exists():
            for s in all_students:
                print(f"      ⚠️ وُجد في شعبة أخرى: {s.full_name} (الشعبة ID: {s.section.id})")
        else:
            print("      ❌ غير موجود في أي شعبة!")
    
except Project.DoesNotExist:
    print("   ❌ المشروع 5 غير موجود!")

print()
print("=" * 60)
