import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration
from django.db.models import Count, Q

print("\n" + "=" * 80)
print("📊 تحليل حالة الطلاب في Telegram")
print("=" * 80)

# إحصائيات عامة
total_students = StudentRegistration.objects.count()
joined = StudentRegistration.objects.filter(joined_telegram=True).count()
not_joined = StudentRegistration.objects.filter(joined_telegram=False).count()
with_username = StudentRegistration.objects.filter(telegram_username__isnull=False).exclude(telegram_username='').count()

print(f"\n📈 الإحصائيات العامة:")
print(f"   • إجمالي الطلاب: {total_students}")
print(f"   • انضموا للتليجرام: {joined} ({round(joined/total_students*100, 1) if total_students > 0 else 0}%)")
print(f"   • لم ينضموا: {not_joined} ({round(not_joined/total_students*100, 1) if total_students > 0 else 0}%)")
print(f"   • لديهم username: {with_username}")

print("\n" + "=" * 80)
print("📋 تفاصيل الطلاب:")
print("=" * 80)

students = StudentRegistration.objects.all().order_by('section__section_name', 'full_name')

for student in students:
    status_emoji = "✅" if student.joined_telegram else "⏳"
    print(f"\n{status_emoji} {student.full_name}")
    print(f"   📚 الشعبة: {student.section.section_name}")
    print(f"   📱 حالة التليجرام: {'انضم' if student.joined_telegram else 'لم ينضم'}")
    
    if student.joined_telegram:
        print(f"   👤 Username: @{student.telegram_username or 'غير متوفر'}")
        print(f"   🆔 User ID: {student.telegram_user_id or 'غير متوفر'}")
        print(f"   📅 تاريخ الانضمام: {student.joined_at.strftime('%Y-%m-%d %H:%M') if student.joined_at else 'غير متوفر'}")
    else:
        print(f"   ⏳ لم ينضم بعد")

print("\n" + "=" * 80)
print("\n💡 الاقتراحات:")
print("=" * 80)

if not_joined > 0:
    print(f"\n1️⃣ يوجد {not_joined} طالب لم ينضموا للتليجرام بعد")
    print("   الحل:")
    print("   • أرسل لهم روابط join.html")
    print("   • تأكد من تشغيل Bot (python telegram_welcome_bot.py)")

if joined > 0 and with_username < joined:
    missing_usernames = joined - with_username
    print(f"\n2️⃣ يوجد {missing_usernames} طالب انضموا لكن بدون username")
    print("   السبب: قد لا يكون لديهم username على Telegram")

if joined == 0:
    print("\n⚠️  لا يوجد طلاب انضموا للتليجرام بعد!")
    print("   الحل:")
    print("   1. تأكد من تشغيل Backend: python manage.py runserver")
    print("   2. تأكد من تشغيل Bot: python telegram_welcome_bot.py")
    print("   3. أرسل رابط join.html للطلاب")

print("\n" + "=" * 80)

# إحصائيات حسب الشعبة
print("\n📊 إحصائيات حسب الشعبة:")
print("=" * 80)

sections_stats = StudentRegistration.objects.values('section__section_name').annotate(
    total=Count('id'),
    joined=Count('id', filter=Q(joined_telegram=True)),
    not_joined=Count('id', filter=Q(joined_telegram=False))
).order_by('section__section_name')

for section in sections_stats:
    section_name = section['section__section_name']
    total = section['total']
    joined = section['joined']
    not_joined = section['not_joined']
    percentage = round(joined/total*100, 1) if total > 0 else 0
    
    print(f"\n📖 الشعبة {section_name}:")
    print(f"   • الإجمالي: {total}")
    print(f"   • انضموا: {joined} ({percentage}%)")
    print(f"   • لم ينضموا: {not_joined}")

print("\n" + "=" * 80)
