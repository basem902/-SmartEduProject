"""
Django Management Command لإنشاء قروبات تيليجرام
يعمل بشكل مستقل خارج Django request cycle
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'إنشاء قروبات تيليجرام باستخدام Pyrogram Client API'

    def add_arguments(self, parser):
        parser.add_argument('grade_name', type=str, help='اسم الصف')
        parser.add_argument('subject_name', type=str, help='اسم المادة')
        parser.add_argument('sections', type=str, help='الشُعب مفصولة بفواصل (مثال: أ,ب,ج)')
        parser.add_argument('phone_number', type=str, help='رقم الهاتف')
        parser.add_argument('--bot', type=str, required=False, help='اسم مستخدم البوت (اختياري)')
        parser.add_argument('--school', type=str, required=False, help='اسم المدرسة (اختياري)')

    def handle(self, *args, **options):
        grade_name = options['grade_name']
        subject_name = options['subject_name']
        sections_str = options['sections']
        phone_number = options['phone_number']
        bot_username = options.get('bot')
        school_name = options.get('school')
        
        # تحويل الشُعب إلى قائمة
        sections = [s.strip() for s in sections_str.split(',')]
        
        self.stdout.write(self.style.SUCCESS(f'\n🚀 بدء إنشاء {len(sections)} قروب...\n'))
        
        # استيراد الـ helper
        from apps.sections.telegram_client import create_telegram_groups_with_client
        
        try:
            # الحصول على credentials
            api_id = settings.TELEGRAM_API_ID
            api_hash = settings.TELEGRAM_API_HASH
            
            # إنشاء القروبات
            results = create_telegram_groups_with_client(
                api_id=api_id,
                api_hash=api_hash,
                phone_number=phone_number,
                grade_name=grade_name,
                subject_name=subject_name,
                sections=sections,
                bot_username=bot_username,
                school_name=school_name
            )
            
            # عرض النتائج
            success_count = sum(1 for r in results if r.get('success'))
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ النتائج:\n'))
            self.stdout.write(f'   نجح: {success_count}/{len(results)}\n')
            
            for result in results:
                if result.get('success'):
                    self.stdout.write(self.style.SUCCESS(
                        f"   ✅ {result['group_name']}\n"
                        f"      الرابط: {result['invite_link']}\n"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"   ❌ {result.get('group_name', 'Unknown')}\n"
                        f"      الخطأ: {result.get('error')}\n"
                    ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ خطأ: {e}\n'))
            sys.exit(1)
