import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration

student = StudentRegistration.objects.get(id=9)

print("\n📋 محمد باسم محمد الحجري")
print("=" * 60)
print(f"ID: {student.id}")
print(f"الاسم: {student.full_name}")
print(f"الشعبة: {student.section.section_name}")
print()
print(f"📱 حالة Telegram:")
print(f"   joined_telegram: {student.joined_telegram}")
print(f"   telegram_user_id: {student.telegram_user_id}")
print(f"   telegram_username: {student.telegram_username}")
print(f"   joined_at: {student.joined_at}")
print()

if student.joined_telegram:
    print("✅ تم تحديث البيانات - الطالب انضم للتليجرام!")
else:
    print("⏳ البيانات لم تُحدّث بعد")
    print("💡 تأكد أن Bot يعمل: python telegram_welcome_bot.py")
