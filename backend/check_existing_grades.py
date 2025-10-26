#!/usr/bin/env python
"""
فحص الصفوف الموجودة في قاعدة البيانات
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import SchoolGrade, Section
from apps.accounts.models import Teacher

print("=" * 60)
print("📊 فحص الصفوف الدراسية الموجودة")
print("=" * 60)

# جلب جميع المعلمين
teachers = Teacher.objects.all()
print(f"\n👨‍🏫 عدد المعلمين: {teachers.count()}")

for teacher in teachers:
    grades = SchoolGrade.objects.filter(teacher=teacher)
    print(f"\n{'='*50}")
    print(f"👤 المعلم: {teacher.full_name} ({teacher.email})")
    print(f"   ID: {teacher.id}")
    print(f"   عدد الصفوف: {grades.count()}")
    
    if grades.exists():
        for grade in grades:
            sections_count = grade.sections.count()
            print(f"\n   📚 الصف:")
            print(f"      - ID: {grade.id}")
            print(f"      - المرحلة: {grade.get_level_display()}")
            print(f"      - رقم الصف: {grade.grade_number}")
            print(f"      - المادة: {grade.subject}")
            print(f"      - المدرسة: {grade.school_name}")
            print(f"      - عدد الشُعب: {sections_count}")
            print(f"      - نشط: {'✅' if grade.is_active else '❌'}")
            print(f"      - تاريخ الإنشاء: {grade.created_at}")
            
            # عرض الشُعب
            if sections_count > 0:
                sections = grade.sections.all()[:5]  # أول 5 شعب
                print(f"      - الشُعب: ", end="")
                print(", ".join([s.section_name for s in sections]))
                if sections_count > 5:
                    print(f"        ... و {sections_count - 5} شعبة أخرى")

print("\n" + "=" * 60)
print("📈 الإحصائيات الإجمالية:")
print("=" * 60)

total_grades = SchoolGrade.objects.count()
total_sections = Section.objects.count()
active_grades = SchoolGrade.objects.filter(is_active=True).count()

print(f"📊 الصفوف: {total_grades} (نشط: {active_grades})")
print(f"📊 الشُعب: {total_sections}")

# البحث عن الصف المكرر المحتمل
print("\n" + "=" * 60)
print("🔍 البحث عن الصفوف المكررة:")
print("=" * 60)

from django.db.models import Count

duplicates = SchoolGrade.objects.values(
    'teacher', 'level', 'grade_number', 'subject'
).annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicates.exists():
    print("⚠️ توجد صفوف مكررة:")
    for dup in duplicates:
        print(f"\n   المعلم ID: {dup['teacher']}")
        print(f"   المرحلة: {dup['level']}")
        print(f"   رقم الصف: {dup['grade_number']}")
        print(f"   المادة: {dup['subject']}")
        print(f"   عدد التكرارات: {dup['count']}")
        
        # عرض السجلات المكررة
        duped_grades = SchoolGrade.objects.filter(
            teacher_id=dup['teacher'],
            level=dup['level'],
            grade_number=dup['grade_number'],
            subject=dup['subject']
        )
        
        for grade in duped_grades:
            print(f"      → ID: {grade.id}, المدرسة: {grade.school_name}, الشُعب: {grade.sections.count()}")
else:
    print("✅ لا توجد صفوف مكررة")

print("\n" + "=" * 60)
