"""
Script to update teacher's Telegram ID
"""
import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import Teacher

# معرف تيليجرام الخاص بك
TELEGRAM_ID = 5844908352

# تحديث المعلم basem902 (سنجرب عدة طرق للعثور عليه)
try:
    # محاولة 1: البحث بالبريد
    teacher = Teacher.objects.filter(email__icontains='basem').first()
    
    if not teacher:
        # محاولة 2: أول معلم في القاعدة
        teacher = Teacher.objects.first()
    
    if not teacher:
        print("❌ لا يوجد معلمون في قاعدة البيانات")
        sys.exit(1)
    teacher.telegram_id = TELEGRAM_ID
    teacher.save()
    print(f"✅ تم تحديث معرف تيليجرام للمعلم {teacher.full_name}")
    print(f"   Telegram ID: {teacher.telegram_id}")
except Teacher.DoesNotExist:
    print("❌ لم يتم العثور على المعلم")
except Exception as e:
    print(f"❌ خطأ: {e}")
