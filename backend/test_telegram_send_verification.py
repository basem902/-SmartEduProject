"""
اختبار شامل لإرسال رسائل التيليجرام - للتحقق من المشاكل
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
import requests
from apps.projects.telegram_helper import TelegramProjectNotifier


def test_bot_token():
    """اختبار صحة Bot Token"""
    print("\n" + "=" * 60)
    print("🔍 اختبار 1: التحقق من Bot Token")
    print("=" * 60)
    
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    
    if not token:
        print("❌ فشل: TELEGRAM_BOT_TOKEN غير موجود في .env")
        print("   → تأكد من إضافة TELEGRAM_BOT_TOKEN في ملف .env")
        return False
    
    print(f"✅ Token موجود: {token[:10]}...{token[-10:]}")
    
    # Test token validity
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=5)
        result = response.json()
        
        if result.get('ok'):
            bot_info = result.get('result', {})
            print(f"✅ Token صحيح!")
            print(f"   🤖 Bot Username: @{bot_info.get('username')}")
            print(f"   📛 Bot Name: {bot_info.get('first_name')}")
            print(f"   🆔 Bot ID: {bot_info.get('id')}")
            return True
        else:
            print(f"❌ Token غير صحيح!")
            print(f"   Error: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        return False


def test_telegram_groups():
    """اختبار المجموعات المسجلة"""
    print("\n" + "=" * 60)
    print("🔍 اختبار 2: المجموعات المسجلة في قاعدة البيانات")
    print("=" * 60)
    
    from apps.sections.models import TelegramGroup
    
    groups = TelegramGroup.objects.all()
    print(f"📊 عدد المجموعات المسجلة: {groups.count()}")
    
    if groups.count() == 0:
        print("⚠️ لا توجد مجموعات تيليجرام مسجلة!")
        print("   → قم بإنشاء المجموعات أولاً")
        return False
    
    print("\n📋 قائمة المجموعات:")
    for i, group in enumerate(groups[:10], 1):  # Show first 10 only
        print(f"\n{i}. {group.section.section_name if group.section else 'N/A'}")
        print(f"   📛 Group Name: {group.group_name}")
        print(f"   🆔 Chat ID: {group.chat_id}")
        print(f"   🤖 Bot: @{group.bot_username if group.bot_username else 'N/A'}")
        print(f"   📊 Status: {group.status}")
        print(f"   🔗 Link: {group.invite_link if group.invite_link else 'N/A'}")
    
    if groups.count() > 10:
        print(f"\n... وعدد {groups.count() - 10} مجموعة أخرى")
    
    return True


def test_bot_in_groups():
    """اختبار وجود البوت في المجموعات"""
    print("\n" + "=" * 60)
    print("🔍 اختبار 3: التحقق من وجود البوت في المجموعات")
    print("=" * 60)
    
    from apps.sections.models import TelegramGroup
    
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        print("❌ Token غير موجود، لا يمكن المتابعة")
        return False
    
    # Get bot ID
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url, timeout=5)
    bot_info = response.json().get('result', {})
    bot_id = bot_info.get('id')
    
    if not bot_id:
        print("❌ فشل الحصول على معلومات البوت")
        return False
    
    groups = TelegramGroup.objects.all()[:5]  # Test first 5 groups
    
    success_count = 0
    failed_count = 0
    
    for group in groups:
        print(f"\n📱 اختبار المجموعة: {group.section.section_name if group.section else 'N/A'}")
        print(f"   🆔 Chat ID: {group.chat_id}")
        
        try:
            check_url = f"https://api.telegram.org/bot{token}/getChatMember"
            data = {
                'chat_id': group.chat_id,
                'user_id': bot_id
            }
            
            response = requests.post(check_url, json=data, timeout=5)
            result = response.json()
            
            if result.get('ok'):
                member = result.get('result', {})
                status = member.get('status')
                print(f"   ✅ البوت موجود في المجموعة")
                print(f"   👤 Status: {status}")
                success_count += 1
            else:
                error_desc = result.get('description', 'Unknown')
                print(f"   ❌ البوت غير موجود أو لا يملك صلاحيات")
                print(f"   📄 Error: {error_desc}")
                failed_count += 1
        except Exception as e:
            print(f"   ❌ خطأ: {str(e)}")
            failed_count += 1
    
    print(f"\n📊 النتيجة:")
    print(f"   ✅ نجح: {success_count}")
    print(f"   ❌ فشل: {failed_count}")
    
    return success_count > 0


def test_send_message():
    """اختبار إرسال رسالة تجريبية"""
    print("\n" + "=" * 60)
    print("🔍 اختبار 4: إرسال رسالة تجريبية")
    print("=" * 60)
    
    from apps.sections.models import TelegramGroup
    
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        print("❌ Token غير موجود")
        return False
    
    # Get first group with chat_id
    group = TelegramGroup.objects.filter(chat_id__isnull=False).first()
    
    if not group:
        print("❌ لا توجد مجموعات بها chat_id")
        return False
    
    print(f"📱 إرسال رسالة تجريبية إلى: {group.section.section_name if group.section else 'N/A'}")
    print(f"   🆔 Chat ID: {group.chat_id}")
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': group.chat_id,
            'text': '🧪 <b>رسالة اختبار</b>\n\nهذه رسالة اختبار للتأكد من عمل البوت بشكل صحيح.\n\n✅ إذا وصلتك هذه الرسالة، فالبوت يعمل!',
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        print(f"\n📊 HTTP Status: {response.status_code}")
        print(f"📦 Response OK: {result.get('ok')}")
        
        if result.get('ok'):
            msg = result.get('result', {})
            message_id = msg.get('message_id')
            chat_info = msg.get('chat', {})
            
            print(f"\n✅ نجح الإرسال!")
            print(f"   📨 Message ID: {message_id}")
            print(f"   💬 Chat Title: {chat_info.get('title', 'N/A')}")
            print(f"   🆔 Chat ID: {chat_info.get('id')}")
            print(f"\n✅ تحقق من المجموعة على التيليجرام!")
            return True
        else:
            error_desc = result.get('description', 'Unknown')
            error_code = result.get('error_code', 'N/A')
            print(f"\n❌ فشل الإرسال!")
            print(f"   Error Code: {error_code}")
            print(f"   Description: {error_desc}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        return False


def main():
    """تشغيل جميع الاختبارات"""
    print("\n" + "=" * 60)
    print("🚀 بدء اختبارات التيليجرام الشاملة")
    print("=" * 60)
    
    results = {
        'bot_token': test_bot_token(),
        'telegram_groups': test_telegram_groups(),
        'bot_in_groups': test_bot_in_groups(),
        'send_message': test_send_message()
    }
    
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج")
    print("=" * 60)
    
    print(f"1. Bot Token: {'✅ صحيح' if results['bot_token'] else '❌ فشل'}")
    print(f"2. مجموعات مسجلة: {'✅ موجودة' if results['telegram_groups'] else '❌ غير موجودة'}")
    print(f"3. البوت في المجموعات: {'✅ موجود' if results['bot_in_groups'] else '❌ غير موجود'}")
    print(f"4. إرسال رسالة تجريبية: {'✅ نجح' if results['send_message'] else '❌ فشل'}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 جميع الاختبارات نجحت! النظام جاهز للإرسال")
    else:
        print("⚠️ بعض الاختبارات فشلت - راجع التفاصيل أعلاه")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ تم إيقاف الاختبار")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ خطأ غير متوقع: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
