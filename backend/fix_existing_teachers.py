"""
Link existing teachers to User accounts
"""
import os
import sys
import django

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import Teacher

print("=" * 60)
print("Linking Teachers to User accounts")
print("=" * 60)

# الحصول على جميع المعلمين بدون user
teachers_without_user = Teacher.objects.filter(user__isnull=True)

print(f"\nTeachers without User account: {teachers_without_user.count()}")

for teacher in teachers_without_user:
    print(f"\nProcessing: {teacher.full_name} ({teacher.email})")
    
    # Check if User exists with same email
    user = User.objects.filter(email=teacher.email).first()
    
    if user:
        print(f"  User already exists: {user.username}")
        teacher.user = user
        teacher.save()
        print(f"  Linked successfully!")
    else:
        # Create new User
        username = teacher.email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # كلمة مرور مؤقتة (نفس password_hash للمعلم)
        user = User.objects.create(
            username=username,
            email=teacher.email,
            first_name=teacher.full_name
        )
        # Copy password from teacher
        user.password = teacher.password_hash
        user.save()
        
        teacher.user = user
        teacher.save()
        
        print(f"  New User created: {username}")
        print(f"  Linked successfully!")

print("\n" + "=" * 60)
print("DONE!")
print("=" * 60)
print("\nYou can now login with your existing accounts")
