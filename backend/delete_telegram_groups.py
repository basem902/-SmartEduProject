"""
حذف جميع مجموعات التيليجرام من قاعدة البيانات
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
    print("🗑️ حذف مجموعات التيليجرام من قاعدة البيانات")
    print("=" * 60)
    
    groups = TelegramGroup.objects.all()
    count = groups.count()
    
    if count == 0:
        print("\n✅ لا توجد مجموعات في قاعدة البيانات")
        return
    
    print(f"\n📊 عدد المجموعات المسجلة: {count}")
    print("\n📋 المجموعات:")
    
    for i, group in enumerate(groups, 1):
        print(f"   {i}. {group.group_name} (Section ID: {group.section_id})")
    
    print("\n⚠️ تحذير: هذا سيحذف البيانات من قاعدة البيانات فقط")
    print("   المجموعات على التيليجرام ستبقى موجودة")
    print("   يمكنك إعادة إنشاء السجلات بعد ذلك")
    
    confirm = input("\n❓ هل أنت متأكد من الحذف؟ (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y', 'نعم']:
        print("\n🗑️ جاري الحذف...")
        deleted_count = groups.count()
        groups.delete()
        
        print(f"✅ تم حذف {deleted_count} مجموعة من قاعدة البيانات")
        print("\n🔄 الخطوة التالية:")
        print("   شغّل: python create_groups_telethon.py")
        print("   أو: python create_groups_standalone.py")
        print("   لإعادة إنشاء المجموعات بشكل صحيح")
    else:
        print("\n❌ تم الإلغاء - لم يتم حذف أي شيء")
    
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
