#!/usr/bin/env python
"""
اختبار إرسال رسالة Telegram
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup
from apps.projects.telegram_helper import TelegramProjectNotifier

print("=" * 60)
print("🧪 اختبار إرسال رسالة Telegram")
print("=" * 60)

# جلب أول قروب
group = TelegramGroup.objects.first()

if not group:
    print("❌ لا توجد قروبات!")
    exit(1)

print(f"\n📱 القروب: {group.group_name}")
print(f"   - chat_id: {group.chat_id}")
print(f"   - invite_link: {group.invite_link[:50]}...")
print(f"   - is_bot_added: {group.is_bot_added}")
print(f"   - is_bot_admin: {group.is_bot_admin}")

# بيانات مشروع تجريبي
project_data = {
    'id': 999,
    'title': 'مشروع اختبار',
    'subject': 'المهارات الرقمية',
    'description': 'هذا مشروع تجريبي للاختبار',
    'instructions': '1️⃣ الخطوة الأولى\n2️⃣ الخطوة الثانية\n3️⃣ الخطوة الثالثة',
    'requirements': '1️⃣ المتطلب الأول\n2️⃣ المتطلب الثاني',
    'tips': '💡 نصيحة 1\n💡 نصيحة 2',
    'deadline': '2025-11-01',
    'max_score': 20,
    'file_types': 'pdf,docx',
    'max_file_size': 5,
    'allow_late_submission': False,
    'submission_url': 'http://localhost:5500/submit/test-token'
}

section_data = {
    'id': group.section.id,
    'section_name': group.section.section_name,
    'grade': {
        'display_name': group.section.grade.display_name
    }
}

print("\n🚀 محاولة إرسال الرسالة...")
print("-" * 60)

try:
    # إنشاء mock project object
    class MockProject:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    mock_project = MockProject(project_data)
    
    # استخدام TelegramProjectNotifier
    notifier = TelegramProjectNotifier()
    
    # اختبار بسيط: إرسال رسالة
    import requests
    api_url = f"https://api.telegram.org/bot{notifier.bot_token}"
    
    message_text = f"""
📚 ━━━━━━ مشروع تجريبي ━━━━━━ 📚

📌 العنوان: {project_data['title']}
📖 المادة: {project_data['subject']}

━━━━━━━━━━━━━━━━━━━━━━

هذه رسالة اختبار من SmartEdu!

🎯 الدرجة الكاملة: {project_data['max_score']} درجة
"""
    
    response = requests.post(
        f"{api_url}/sendMessage",
        json={
            'chat_id': group.chat_id,
            'text': message_text,
            'parse_mode': 'HTML'
        }
    )
    
    result = response.json()
    
    print("\n📊 النتيجة:")
    print(f"   - ok: {result.get('ok')}")
    print(f"   - message_id: {result.get('result', {}).get('message_id')}")
    
    if result.get('ok'):
        print("\n✅ تم الإرسال بنجاح!")
        print(f"   افتح Telegram وتحقق من القروب!")
    else:
        print("\n❌ فشل الإرسال!")
        print(f"   السبب: {result.get('description')}")
        print(f"   الكود: {result.get('error_code')}")
        
except Exception as e:
    print(f"\n❌ خطأ: {str(e)}")
    import traceback
    print("\n🔍 Traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)
