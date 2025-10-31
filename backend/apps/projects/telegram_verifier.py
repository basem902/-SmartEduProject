"""
📱 Telegram Group Verification - التحقق الحي من عضوية القروب
يتحقق مباشرة من Telegram API أن الطالب عضو في القروب
"""
import logging
import os
from telegram import Bot
from telegram.error import TelegramError
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramGroupVerifier:
    """
    التحقق من عضوية الطالب في قروب التليجرام
    """
    
    def __init__(self):
        """تهيئة البوت"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or settings.TELEGRAM_BOT_TOKEN
        if not self.bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN غير موجود!")
            self.bot = None
        else:
            self.bot = Bot(token=self.bot_token)
    
    async def is_member(self, chat_id, user_id):
        """
        التحقق من أن المستخدم عضو في القروب
        
        Args:
            chat_id: معرف القروب (يبدأ بـ -)
            user_id: معرف المستخدم في تليجرام
            
        Returns:
            dict: {
                'is_member': bool,
                'status': str,  # member, administrator, creator, left, kicked
                'user_info': dict or None
            }
        """
        if not self.bot:
            return {
                'is_member': False,
                'status': 'bot_not_configured',
                'error': 'البوت غير مُعد بشكل صحيح'
            }
        
        try:
            # الحصول على معلومات العضوية
            member = await self.bot.get_chat_member(chat_id, user_id)
            
            # الحالات المقبولة
            valid_statuses = ['member', 'administrator', 'creator']
            is_valid_member = member.status in valid_statuses
            
            logger.info(f"✅ التحقق من العضوية: user_id={user_id}, chat_id={chat_id}, status={member.status}")
            
            return {
                'is_member': is_valid_member,
                'status': member.status,
                'user_info': {
                    'user_id': member.user.id,
                    'first_name': member.user.first_name,
                    'last_name': member.user.last_name,
                    'username': member.user.username
                } if is_valid_member else None
            }
            
        except TelegramError as e:
            error_msg = str(e).lower()
            
            # حالات خاصة
            if 'user not found' in error_msg or 'chat not found' in error_msg:
                logger.warning(f"⚠️ المستخدم أو القروب غير موجود: {e}")
                return {
                    'is_member': False,
                    'status': 'not_found',
                    'error': 'المستخدم أو القروب غير موجود'
                }
            elif 'forbidden' in error_msg:
                logger.error(f"❌ البوت ليس عضواً في القروب أو ليس لديه صلاحيات: {e}")
                return {
                    'is_member': False,
                    'status': 'bot_no_permission',
                    'error': 'البوت ليس عضواً في القروب'
                }
            else:
                logger.error(f"❌ خطأ في التحقق من العضوية: {e}", exc_info=True)
                return {
                    'is_member': False,
                    'status': 'error',
                    'error': str(e)
                }
    
    async def verify_student_membership(self, student, group_chat_id):
        """
        التحقق الكامل من عضوية الطالب
        
        Args:
            student: كائن StudentRegistration
            group_chat_id: معرف القروب
            
        Returns:
            dict: {
                'verified': bool,
                'status': str,
                'message': str,
                'telegram_info': dict or None
            }
        """
        # 1. التحقق من أن الطالب لديه telegram_user_id
        if not student.telegram_user_id:
            return {
                'verified': False,
                'status': 'no_telegram_id',
                'message': 'الطالب لم يربط حسابه بالبوت بعد',
                'action': 'يجب على الطالب إرسال /start للبوت أولاً'
            }
        
        # 2. التحقق من العضوية مباشرة من Telegram
        membership = await self.is_member(group_chat_id, student.telegram_user_id)
        
        if membership['is_member']:
            # ✅ عضو نشط
            return {
                'verified': True,
                'status': 'active_member',
                'message': f'الطالب {student.full_name} عضو نشط في القروب',
                'telegram_info': membership['user_info']
            }
        else:
            # ❌ غير عضو
            status = membership['status']
            
            if status == 'left':
                message = 'الطالب خرج من القروب'
                action = 'يجب عليه الانضمام مرة أخرى'
            elif status == 'kicked':
                message = 'الطالب محظور من القروب'
                action = 'تواصل مع المعلم لإعادة الإضافة'
            elif status == 'not_found':
                message = 'الطالب غير موجود في القروب'
                action = 'يجب عليه الانضمام إلى القروب'
            elif status == 'bot_no_permission':
                message = 'البوت ليس عضواً في القروب أو ليس لديه صلاحيات'
                action = 'تواصل مع المعلم لإضافة البوت كمشرف'
            else:
                message = 'لم نتمكن من التحقق من العضوية'
                action = 'حاول مرة أخرى أو تواصل مع الدعم الفني'
            
            return {
                'verified': False,
                'status': status,
                'message': message,
                'action': action,
                'error': membership.get('error')
            }
    
    async def get_group_members_count(self, chat_id):
        """
        الحصول على عدد أعضاء القروب
        
        Args:
            chat_id: معرف القروب
            
        Returns:
            int or None: عدد الأعضاء
        """
        if not self.bot:
            return None
        
        try:
            chat = await self.bot.get_chat(chat_id)
            return chat.member_count
        except TelegramError as e:
            logger.error(f"❌ فشل الحصول على عدد الأعضاء: {e}")
            return None
    
    async def get_group_info(self, chat_id):
        """
        الحصول على معلومات القروب
        
        Args:
            chat_id: معرف القروب
            
        Returns:
            dict or None: معلومات القروب
        """
        if not self.bot:
            return None
        
        try:
            chat = await self.bot.get_chat(chat_id)
            return {
                'id': chat.id,
                'title': chat.title,
                'type': chat.type,
                'description': chat.description,
                'member_count': chat.member_count,
                'invite_link': chat.invite_link
            }
        except TelegramError as e:
            logger.error(f"❌ فشل الحصول على معلومات القروب: {e}")
            return None


def verify_student_in_group_sync(student, group_chat_id):
    """
    نسخة Sync من verify_student_membership (للاستخدام في Django views)
    
    Args:
        student: كائن StudentRegistration
        group_chat_id: معرف القروب
        
    Returns:
        dict: نتيجة التحقق
    """
    import asyncio
    
    verifier = TelegramGroupVerifier()
    
    # تشغيل الدالة الـ async
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            verifier.verify_student_membership(student, group_chat_id)
        )
        return result
    finally:
        loop.close()


def is_member_sync(chat_id, user_id):
    """
    نسخة Sync من is_member (للاستخدام في Django views)
    
    Args:
        chat_id: معرف القروب
        user_id: معرف المستخدم
        
    Returns:
        dict: نتيجة التحقق
    """
    import asyncio
    
    verifier = TelegramGroupVerifier()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            verifier.is_member(chat_id, user_id)
        )
        return result
    finally:
        loop.close()
