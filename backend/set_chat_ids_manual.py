"""
إدخال Chat IDs يدوياً للمجموعات
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import TelegramGroup


def main():
    print("\n" + "=" * 60)
    print("📝 إدخال Chat IDs يدوياً")
    print("=" * 60)
    
    print("\n💡 كيفية الحصول على Chat ID:")
    print("   1. افتح المجموعة في تيليجرام")
    print("   2. أضف البوت @getidsbot للمجموعة")
    print("   3. اكتب: /id@getidsbot")
    print("   4. انسخ Chat ID (رقم سالب يبدأ بـ -100)")
    print()
    
    groups = TelegramGroup.objects.filter(chat_id__isnull=True).order_by('id')
    
    if groups.count() == 0:
        print("✅ جميع المجموعات لديها Chat ID!")
        return
    
    print(f"📊 المجموعات التي تحتاج Chat ID: {groups.count()}\n")
    
    for group in groups:
        print("=" * 60)
        print(f"📱 المجموعة: {group.group_name}")
        print(f"   🆔 Section ID: {group.section_id}")
        print(f"   🔗 الرابط: {group.invite_link}")
        print()
        
        while True:
            chat_id_input = input("   أدخل Chat ID (أو اكتب 'skip' للتخطي): ").strip()
            
            if chat_id_input.lower() == 'skip':
                print("   ⏭️ تم التخطي\n")
                break
            
            # التحقق من الإدخال
            try:
                chat_id = int(chat_id_input)
                
                # التحقق من أن chat_id صحيح (سالب ويبدأ بـ -100)
                if chat_id >= 0:
                    print("   ❌ خطأ: Chat ID يجب أن يكون رقم سالب!")
                    continue
                
                if not str(chat_id).startswith('-100'):
                    print("   ⚠️ تحذير: Chat ID عادة يبدأ بـ -100")
                    confirm = input("   هل أنت متأكد من هذا الرقم؟ (yes/no): ")
                    if confirm.lower() not in ['yes', 'y', 'نعم']:
                        continue
                
                # حفظ Chat ID
                group.chat_id = chat_id
                group.status = 'created'
                group.save()
                
                print(f"   ✅ تم الحفظ: {chat_id}\n")
                break
                
            except ValueError:
                print("   ❌ خطأ: يجب إدخال رقم صحيح!")
                continue
    
    # عرض النتائج النهائية
    print("\n" + "=" * 60)
    print("📊 النتيجة النهائية:")
    print("=" * 60)
    
    all_groups = TelegramGroup.objects.all()
    with_chat_id = all_groups.filter(chat_id__isnull=False).count()
    without_chat_id = all_groups.filter(chat_id__isnull=True).count()
    
    print(f"✅ لديها Chat ID: {with_chat_id}")
    print(f"⚠️ بدون Chat ID: {without_chat_id}")
    print(f"📊 المجموع: {all_groups.count()}")
    
    if without_chat_id == 0:
        print("\n🎉 ممتاز! جميع المجموعات الآن لديها Chat ID")
        print("\n🔄 الخطوة التالية:")
        print("   شغّل: python test_telegram_send_verification.py")
        print("   للتحقق من أن كل شيء يعمل!")
    
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
