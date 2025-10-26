"""
إضافة معلم تجريبي للاختبار
"""
import os
import django

# تحميل إعدادات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import Teacher, Settings

# معلومات المعلم التجريبي
email = "teacher@test.com"
password = "Test@123456"

# التحقق من عدم وجود المعلم
if Teacher.objects.filter(email=email).exists():
    print(f"❌ المعلم {email} موجود مسبقاً!")
    teacher = Teacher.objects.get(email=email)
else:
    # إنشاء المعلم
    teacher = Teacher.objects.create(
        full_name="معلم تجريبي",
        email=email,
        phone="0501234567",
        school_name="مدرسة الاختبار"
    )
    teacher.set_password(password)
    teacher.save()
    
    # إنشاء إعدادات افتراضية
    Settings.objects.create(teacher=teacher)
    
    print("✅ تم إنشاء المعلم التجريبي بنجاح!")

print(f"""
📧 البريد: {email}
🔐 كلمة المرور: {password}
""")
