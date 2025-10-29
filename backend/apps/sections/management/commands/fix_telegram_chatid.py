"""
Django Management Command: Fix Telegram chat_id
تصحيح chat_id من موجب إلى سالب (-100 prefix)

Usage:
    python manage.py fix_telegram_chatid
    python manage.py fix_telegram_chatid --dry-run
"""
from django.core.management.base import BaseCommand
from apps.sections.models import TelegramGroup


class Command(BaseCommand):
    help = 'Fix Telegram Group chat_id from positive to negative (-100 prefix)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING('=' * 80))
        self.stdout.write(self.style.WARNING('🔧 Telegram chat_id Fix Utility'))
        self.stdout.write(self.style.WARNING('=' * 80))
        
        # Get all groups with positive chat_id
        groups_to_fix = TelegramGroup.objects.filter(chat_id__gt=0)
        total_count = groups_to_fix.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No groups need fixing. All chat_id values are correct!'))
            return
        
        self.stdout.write(f'\n📊 Found {total_count} groups with positive chat_id\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made\n'))
        
        fixed_count = 0
        failed_count = 0
        
        for group in groups_to_fix:
            old_chat_id = group.chat_id
            # Convert: 3298260616 → -1003298260616
            new_chat_id = int(f'-100{old_chat_id}')
            
            self.stdout.write(f'  • Group #{group.id}: {group.group_name}')
            self.stdout.write(f'    Section: {group.section.section_name if group.section else "N/A"}')
            self.stdout.write(f'    Old chat_id: {old_chat_id}')
            self.stdout.write(f'    New chat_id: {new_chat_id}')
            
            if not dry_run:
                try:
                    group.chat_id = new_chat_id
                    group.save(update_fields=['chat_id'])
                    self.stdout.write(self.style.SUCCESS(f'    ✅ Fixed!\n'))
                    fixed_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ❌ Failed: {str(e)}\n'))
                    failed_count += 1
            else:
                self.stdout.write(self.style.WARNING(f'    🔍 Would be fixed\n'))
                fixed_count += 1
        
        self.stdout.write('\n' + '=' * 80)
        if dry_run:
            self.stdout.write(self.style.WARNING(f'🔍 DRY RUN SUMMARY:'))
            self.stdout.write(f'  • Would fix: {fixed_count} groups')
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ SUMMARY:'))
            self.stdout.write(f'  • Fixed: {fixed_count} groups')
            if failed_count > 0:
                self.stdout.write(self.style.ERROR(f'  • Failed: {failed_count} groups'))
        
        self.stdout.write('=' * 80)
        
        if not dry_run and fixed_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\n✅ All done! {fixed_count} groups fixed successfully.'))
            self.stdout.write('\n💡 Next steps:')
            self.stdout.write('  1. Make sure the bot is added to all groups')
            self.stdout.write('  2. Make the bot an admin with required permissions')
            self.stdout.write('  3. Test sending messages via telegram-send-direct.html')
