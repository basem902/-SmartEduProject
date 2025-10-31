"""
🔐 توليد Token لطالب معين
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import jwt
from django.conf import settings
from datetime import datetime, timedelta
from apps.sections.models import StudentRegistration
from apps.projects.models import Project

print("=" * 60)
print("🔐 توليد Token للطالب")
print("=" * 60)
print()

# اختيار الطالب
print("👥 الطلاب المتاحون:")
students = StudentRegistration.objects.all()
for i, student in enumerate(students, 1):
    print(f"   {i}. {student.full_name} ({student.section.section_name})")

student_choice = int(input("\nاختر رقم الطالب: ")) - 1
selected_student = students[student_choice]

print(f"\n✅ الطالب: {selected_student.full_name}")

# اختيار المشروع
print("\n📁 المشاريع المتاحة:")
projects = Project.objects.all()
for i, project in enumerate(projects, 1):
    print(f"   {i}. {project.title} (ID: {project.id})")

project_choice = int(input("\nاختر رقم المشروع: ")) - 1
selected_project = projects[project_choice]

print(f"\n✅ المشروع: {selected_project.title}")

# توليد Token
upload_token = jwt.encode({
    'student_id': selected_student.id,
    'student_name': selected_student.full_name,
    'project_id': selected_project.id,
    'section_id': selected_student.section.id,
    'exp': datetime.utcnow() + timedelta(days=7),  # صالح لمدة 7 أيام
    'iat': datetime.utcnow()
}, settings.SECRET_KEY, algorithm='HS256')

print()
print("=" * 60)
print("✅ تم توليد الـ Token!")
print("=" * 60)
print()
print("🔗 الرابط الكامل:")
print()
print(f"https://smartedu-basem.netlify.app/pages/submit-project.html?token={upload_token}")
print()
print("📋 أو محلياً:")
print()
print(f"http://localhost:5500/pages/submit-project.html?token={upload_token}")
print()
print("⏰ صالح حتى:", (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M'))
print()
