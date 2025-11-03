import os
import asyncio
import traceback
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.sections.models import TelegramGroup

# Pyrogram
from pyrogram import Client
from pyrogram.types import ChatPrivileges


class Command(BaseCommand):
    help = "Promote the Telegram bot to admin in all groups"

    def handle(self, *args, **options):
        try:
            asyncio.run(self._run())
        except Exception as e:
            # اطبع الأثر الكامل ثم اخرج بكود خطأ ليستقبله الـ API
            self.stdout.write(self.style.WARNING(f"⚠️ حدث استثناء: {e}"))
            tb = traceback.format_exc()
            self.stdout.write(tb)
            raise CommandError(str(e))

    async def _run(self):
        # Locate session file under backend/sessions
        session_dir = os.path.join(settings.BASE_DIR, 'sessions')
        session_file = None
        if os.path.exists(session_dir):
            for filename in os.listdir(session_dir):
                if filename.endswith('.session') and 'session_' in filename:
                    session_file = os.path.join(session_dir, filename[:-8])  # strip .session
                    break

        if not session_file or not os.path.exists(session_file + '.session'):
            self.stdout.write("❌ لا توجد session محفوظة!\n")
            self.stdout.write("💡 الحل: افتح صفحة إنشاء القروبات وسجل الدخول، ثم أعد المحاولة\n")
            return

        self.stdout.write("=" * 80)
        self.stdout.write("🤖 ترقية البوت في جميع المجموعات")
        self.stdout.write("=" * 80)

        client = Client(
            name=session_file,
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH,
        )

        results = {
            'total': 0,
            'success': 0,
            'already_admin': 0,
            'failed': 0,
        }

        async with client:
            # Get bot user
            bot_username = settings.TELEGRAM_BOT_USERNAME.replace('@', '')
            try:
                bot = await client.get_users(f"@{bot_username}")
            except Exception as e:
                self.stdout.write(f"❌ خطأ في الحصول على معلومات البوت: {e}\n")
                return

            groups = TelegramGroup.objects.filter(is_active=True)
            results['total'] = groups.count()
            if results['total'] == 0:
                self.stdout.write("⚠️ لا توجد مجموعات في قاعدة البيانات\n")
                return

            for idx, group in enumerate(groups, 1):
                self.stdout.write(f"[{idx}/{results['total']}] 📱 {group.group_name} (chat_id: {group.chat_id})")
                try:
                    member = await client.get_chat_member(group.chat_id, bot.id)
                    status = getattr(member, 'status', None)
                    status_name = getattr(status, 'name', str(status))

                    if status_name in ("ADMINISTRATOR", "OWNER", "CREATOR"):
                        results['already_admin'] += 1
                        self.stdout.write("   👑 البوت مشرف بالفعل")
                    elif status_name == "MEMBER":
                        await client.promote_chat_member(
                            group.chat_id,
                            bot.id,
                            privileges=ChatPrivileges(
                                can_manage_chat=True,
                                can_delete_messages=True,
                                can_restrict_members=True,
                                can_invite_users=True,
                                can_pin_messages=True,
                            ),
                        )
                        results['success'] += 1
                        group.is_bot_added = True
                        group.is_bot_admin = True
                        group.status = 'bot_admin'
                        group.save(update_fields=["is_bot_added", "is_bot_admin", "status", "updated_at"])
                        self.stdout.write("   ✅ تمت الترقية بنجاح")
                    else:
                        results['failed'] += 1
                        self.stdout.write(f"   ❓ حالة غير متوقعة: {status_name}")
                except Exception as e:
                    results['failed'] += 1
                    self.stdout.write(f"   ❌ فشل: {e}")
                await asyncio.sleep(1)

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("📊 ملخص النتائج:")
        self.stdout.write(f"   🔢 الإجمالي: {results['total']}")
        self.stdout.write(f"   ✅ نجح: {results['success']}")
        self.stdout.write(f"   👑 كان مشرف مسبقاً: {results['already_admin']}")
        self.stdout.write(f"   ❌ فشل: {results['failed']}")
        self.stdout.write("=" * 80 + "\n")
