"""
Script to check and update teacher subjects
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import Teacher

# Get all teachers
teachers = Teacher.objects.all()

print("=" * 60)
print("📊 Teachers and their Subjects")
print("=" * 60)

for teacher in teachers:
    print(f"\n👤 Teacher: {teacher.full_name}")
    print(f"   Email: {teacher.email}")
    print(f"   School: {teacher.school_name}")
    print(f"   Subjects: {teacher.subjects if teacher.subjects else '❌ Empty!'}")
    print("-" * 60)

# Ask if user wants to add default subjects
print("\n" + "=" * 60)
print("Would you like to add default subjects to teachers with empty subjects?")
print("=" * 60)
answer = input("Type 'yes' to continue: ")

if answer.lower() == 'yes':
    default_subjects = [
        'المهارات الرقمية',
        'العلوم',
        'الرياضيات',
        'اللغة العربية',
        'اللغة الإنجليزية',
        'الاجتماعيات',
        'التربية الإسلامية',
        'التربية الفنية',
        'التربية البدنية'
    ]
    
    for teacher in teachers:
        if not teacher.subjects:
            teacher.subjects = default_subjects
            teacher.save()
            print(f"✅ Added subjects to {teacher.full_name}")
    
    print("\n✅ All teachers updated successfully!")
else:
    print("\n❌ Operation cancelled")

print("\n" + "=" * 60)
