"""
إصلاح تنسيق Chat IDs الخاطئة
المشكلة: chat_ids تبدأ بـ -103 بدلاً من -100
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup


def fix_chat_id_format(chat_id):
    """
    تصحيح تنسيق chat_id
    -103238104632 → -1001032381046 (إزالة آخر رقمين وإضافة 100 في البداية)
    """
    if not chat_id:
        return None
    
    chat_id_str = str(chat_id)
    
    # إذا كان يبدأ بـ -103
    if chat_id_str.startswith('-103'):
        # إزالة الـ - والـ 103
        numbers = chat_id_str[4:]  # خذ الباقي بعد -103
        
        # إنشاء chat_id صحيح
        # الـ chat_id الصحيح يجب أن يكون: -100 + الرقم الأصلي
        # لكن يبدو أن الأرقام تم تحويلها بشكل خاطئ
        
        # الطريقة الصحيحة: استخدام الرابط للحصول على chat_id الصحيح
        return None  # سنعيد None لنجبر النظام على استخدام الرابط
    
    return chat_id


def main():
    """إصلاح جميع الـ chat_ids الخاطئة"""
    print("\n" + "=" * 60)
    print("🔧 إصلاح تنسيق Chat IDs")
    print("=" * 60)
    
    groups = TelegramGroup.objects.all()
    print(f"\n📊 عدد المجموعات: {groups.count()}")
    
    fixed_count = 0
    
    print("\n📋 المجموعات ذات Chat IDs الخاطئة:\n")
    
    for group in groups:
        if group.chat_id and str(group.chat_id).startswith('-103'):
            print(f"❌ {group.group_name}")
            print(f"   Chat ID القديم: {group.chat_id}")
            print(f"   الرابط: {group.invite_link}")
            
            # إلغاء الـ chat_id لإجبار النظام على إعادة الحصول عليه
            group.chat_id = None
            group.is_bot_added = False
            group.status = 'created'
            group.save()
            
            print(f"   ✅ تم مسح chat_id - يحتاج إعادة جلب من الرابط")
            fixed_count += 1
            print()
    
    print("=" * 60)
    print(f"✅ تم إصلاح: {fixed_count} مجموعة")
    print("=" * 60)
    
    if fixed_count > 0:
        print("\n🔄 الخطوة التالية:")
        print("   شغّل: python update_chat_ids.py")
        print("   لإعادة جلب chat_ids الصحيحة من روابط المجموعات")
    else:
        print("\n✅ جميع chat_ids بتنسيق صحيح!")
    
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ تم الإيقاف")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
