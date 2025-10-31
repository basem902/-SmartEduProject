"""
📱 إضافة الطلاب التجريبيين إلى قروبات التليجرام الفعلية
ملاحظة: يتطلب Pyrogram (للوصول لـ User Account API)
"""
import os
import sys
import django
import asyncio
from pathlib import Path

# إعداد Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import StudentRegistration, TelegramGroup


async def add_students_to_groups():
    """
    إضافة الطلاب التجريبيين إلى القروبات
    
    ملاحظة: هذا يتطلب:
    1. حساب Telegram User (ليس البوت)
    2. API_ID و API_HASH من my.telegram.org
    3. مكتبة Pyrogram
    """
    
    print("=" * 60)
    print("📱 إضافة طلاب تجريبيين إلى قروبات التليجرام")
    print("=" * 60)
    print()
    
    # التحقق من المكتبات
    try:
        from pyrogram import Client
        from pyrogram.errors import FloodWait, UserAlreadyParticipant
    except ImportError:
        print("❌ خطأ: مكتبة pyrogram غير مثبتة!")
        print()
        print("قم بتثبيتها:")
        print("   pip install pyrogram")
        print()
        return
    
    # التحقق من المتغيرات
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        print("❌ خطأ: TELEGRAM_API_ID و TELEGRAM_API_HASH غير موجودين!")
        print()
        print("احصل عليهما من: https://my.telegram.org")
        print()
        print("ثم أضفهما في ملف .env:")
        print("   TELEGRAM_API_ID=your_api_id")
        print("   TELEGRAM_API_HASH=your_api_hash")
        print()
        return
    
    # إنشاء Client
    app = Client(
        "student_adder",
        api_id=api_id,
        api_hash=api_hash
    )
    
    print("🔐 تسجيل الدخول إلى Telegram...")
    print()
    
    async with app:
        print("✅ تم تسجيل الدخول بنجاح!")
        print()
        
        # جلب جميع القروبات النشطة
        groups = TelegramGroup.objects.filter(is_active=True)
        
        if not groups.exists():
            print("⚠️ لا توجد قروبات نشطة في قاعدة البيانات!")
            return
        
        print(f"📊 وُجد {groups.count()} قروب نشط")
        print()
        
        for group in groups:
            print(f"📱 معالجة القروب: {group.group_name}")
            print(f"   Chat ID: {group.telegram_chat_id}")
            print()
            
            # جلب الطلاب المرتبطين بهذا القروب
            students = StudentRegistration.objects.filter(
                telegram_group=group,
                telegram_username__isnull=False
            )
            
            if not students.exists():
                print("   ⚠️ لا يوجد طلاب مرتبطين بهذا القروب")
                print()
                continue
            
            print(f"   👥 وُجد {students.count()} طالب")
            print()
            
            added = 0
            already_member = 0
            errors = 0
            
            for student in students:
                try:
                    # محاولة إضافة الطالب
                    await app.add_chat_members(
                        chat_id=int(group.telegram_chat_id),
                        user_ids=[student.telegram_username]
                    )
                    
                    print(f"      ✅ {student.full_name} (@{student.telegram_username})")
                    added += 1
                    
                    # تحديث البيانات
                    student.joined_telegram = True
                    student.save()
                    
                    # تأخير لتجنب Flood
                    await asyncio.sleep(2)
                    
                except UserAlreadyParticipant:
                    print(f"      ℹ️ {student.full_name} - عضو مسبقاً")
                    already_member += 1
                    
                    student.joined_telegram = True
                    student.save()
                    
                except FloodWait as e:
                    print(f"      ⏳ انتظار {e.value} ثانية...")
                    await asyncio.sleep(e.value)
                    
                except Exception as e:
                    print(f"      ❌ {student.full_name} - خطأ: {str(e)}")
                    errors += 1
            
            print()
            print(f"   📊 الملخص:")
            print(f"      ✅ تمت الإضافة: {added}")
            print(f"      ℹ️ أعضاء مسبقاً: {already_member}")
            print(f"      ❌ أخطاء: {errors}")
            print()
        
        print("=" * 60)
        print("✅ انتهت عملية الإضافة!")
        print("=" * 60)


async def create_test_group():
    """
    إنشاء قروب تليجرام تجريبي (اختياري)
    """
    try:
        from pyrogram import Client
    except ImportError:
        print("❌ مكتبة pyrogram غير مثبتة!")
        return
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        print("❌ متغيرات Telegram API غير موجودة!")
        return
    
    app = Client("group_creator", api_id=api_id, api_hash=api_hash)
    
    async with app:
        print("🆕 إنشاء قروب تجريبي...")
        
        # إنشاء قروب جديد
        group = await app.create_supergroup(
            title="SmartEdu - اختبار النظام",
            description="قروب تجريبي لاختبار نظام SmartEdu"
        )
        
        print(f"✅ تم إنشاء القروب: {group.title}")
        print(f"   Chat ID: {group.id}")
        print()
        
        # إضافة البوت كمشرف
        bot_username = os.getenv('TELEGRAM_BOT_USERNAME', 'SmartEduProjectBot')
        
        try:
            await app.add_chat_members(
                chat_id=group.id,
                user_ids=[bot_username]
            )
            
            # ترقية البوت لمشرف
            await app.promote_chat_member(
                chat_id=group.id,
                user_id=bot_username,
                privileges={
                    'can_manage_chat': True,
                    'can_delete_messages': True,
                    'can_manage_video_chats': True,
                    'can_restrict_members': True,
                    'can_promote_members': False,
                    'can_change_info': True,
                    'can_invite_users': True,
                    'can_pin_messages': True,
                }
            )
            
            print(f"✅ تم إضافة البوت @{bot_username} كمشرف")
            
        except Exception as e:
            print(f"⚠️ فشل إضافة البوت: {str(e)}")
        
        # الحصول على رابط الدعوة
        try:
            invite_link = await app.export_chat_invite_link(group.id)
            print(f"🔗 رابط الدعوة: {invite_link}")
        except:
            print("⚠️ لم نتمكن من إنشاء رابط دعوة")
        
        print()
        print("💡 استخدم هذه المعلومات في قاعدة البيانات:")
        print(f"   Chat ID: {group.id}")
        print()


def print_instructions():
    """طباعة التعليمات"""
    print("=" * 60)
    print("📱 دليل إضافة طلاب تجريبيين إلى التليجرام")
    print("=" * 60)
    print()
    
    print("🔧 المتطلبات:")
    print("   1. حساب Telegram (ليس البوت)")
    print("   2. API_ID و API_HASH من: https://my.telegram.org")
    print("   3. مكتبة Pyrogram")
    print()
    
    print("📦 التثبيت:")
    print("   pip install pyrogram")
    print()
    
    print("⚙️ الإعداد:")
    print("   أضف في ملف .env:")
    print("   TELEGRAM_API_ID=12345678")
    print("   TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890")
    print()
    
    print("🚀 التشغيل:")
    print("   python add_students_to_telegram.py")
    print()
    
    print("⚠️ ملاحظات:")
    print("   • البوت لا يستطيع إضافة أعضاء، فقط User Account")
    print("   • يجب أن تكون مشرفاً في القروب")
    print("   • قد تحتاج إلى رقم هاتفك للتحقق")
    print("   • التأخير بين الإضافات لتجنب الحظر")
    print()
    
    print("📝 البدائل:")
    print("   1. إنشاء قروب تجريبي جديد")
    print("   2. إرسال روابط دعوة للطلاب")
    print("   3. استخدام أكواد QR")
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='إدارة قروبات التليجرام التجريبية')
    parser.add_argument('--add', action='store_true', help='إضافة الطلاب إلى القروبات')
    parser.add_argument('--create', action='store_true', help='إنشاء قروب تجريبي جديد')
    parser.add_argument('--help-full', action='store_true', help='عرض التعليمات الكاملة')
    
    args = parser.parse_args()
    
    if args.help_full:
        print_instructions()
    elif args.create:
        asyncio.run(create_test_group())
    elif args.add:
        asyncio.run(add_students_to_groups())
    else:
        print("🤖 سكريبت إدارة قروبات التليجرام")
        print()
        print("الاستخدام:")
        print("   python add_students_to_telegram.py --add        # إضافة الطلاب")
        print("   python add_students_to_telegram.py --create     # إنشاء قروب جديد")
        print("   python add_students_to_telegram.py --help-full  # التعليمات الكاملة")
        print()
