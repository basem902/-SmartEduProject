"""
Telegram Client for Creating Groups
Uses Pyrogram (MTProto Client API) instead of Bot API
"""
import logging
import asyncio
from pyrogram import Client
from pyrogram.types import Chat
from pyrogram.errors import FloodWait, BadRequest
import time
import os

logger = logging.getLogger(__name__)


class TelegramGroupCreator:
    """
    إنشاء قروبات تيليجرام باستخدام Client API
    """
    
    def __init__(self, api_id, api_hash, phone_number):
        """
        Initialize Telegram Client
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            phone_number: رقم الهاتف (مع رمز الدولة، مثال: +966xxxxxxxxx)
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        
        # Session directory
        self.session_dir = os.path.join(
            os.path.dirname(__file__), 
            'sessions'
        )
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Session name
        session_name = f"smartedu_{phone_number.replace('+', '').replace(' ', '')}"
        self.session_path = os.path.join(self.session_dir, session_name)
        
        # Client
        self.client = Client(
            self.session_path,
            api_id=self.api_id,
            api_hash=self.api_hash,
            phone_number=self.phone_number
        )
    
    async def create_group(self, group_name, description=None):
        """
        إنشاء قروب تيليجرام
        
        Args:
            group_name: اسم القروب
            description: وصف القروب (اختياري)
            
        Returns:
            dict: معلومات القروب المُنشأ
        """
        try:
            # إنشاء القروب
            chat = await self.client.create_group(
                title=group_name,
                users=[]  # سيتم إضافة الأعضاء لاحقاً
            )
            
            logger.info(f"تم إنشاء القروب: {group_name} (ID: {chat.id})")
            
            # إضافة وصف إذا كان موجود
            if description:
                await self.client.set_chat_description(
                    chat_id=chat.id,
                    description=description
                )
            
            # الحصول على رابط الدعوة
            invite_link = await self.client.export_chat_invite_link(chat.id)
            
            return {
                'success': True,
                'chat_id': chat.id,
                'group_name': group_name,
                'invite_link': invite_link,
                'username': chat.username if hasattr(chat, 'username') else None
            }
            
        except FloodWait as e:
            # انتظر إذا كان هناك rate limiting
            logger.warning(f"FloodWait: انتظر {e.value} ثانية")
            await asyncio.sleep(e.value)
            # حاول مرة أخرى
            return await self.create_group(group_name, description)
            
        except BadRequest as e:
            logger.error(f"خطأ في الطلب: {e}")
            return {
                'success': False,
                'error': f'خطأ في إنشاء القروب: {str(e)}'
            }
            
        except Exception as e:
            logger.error(f"خطأ غير متوقع: {e}")
            return {
                'success': False,
                'error': f'خطأ غير متوقع: {str(e)}'
            }
    
    async def create_multiple_groups(self, groups_data, delay=5):
        """
        إنشاء عدة قروبات
        
        Args:
            groups_data: قائمة من القواميس تحتوي على (name, description)
            delay: التأخير بين كل قروب (بالثواني)
            
        Returns:
            list: نتائج إنشاء القروبات
        """
        results = []
        
        for i, group_info in enumerate(groups_data):
            group_name = group_info.get('name')
            description = group_info.get('description', '')
            
            logger.info(f"إنشاء قروب {i+1}/{len(groups_data)}: {group_name}")
            
            result = await self.create_group(group_name, description)
            results.append(result)
            
            # تأخير بين القروبات (تجنب rate limiting)
            if i < len(groups_data) - 1:
                logger.info(f"انتظار {delay} ثواني قبل القروب التالي...")
                await asyncio.sleep(delay)
        
        return results
    
    async def add_bot_to_group(self, chat_id, bot_username):
        """
        إضافة بوت إلى القروب
        
        Args:
            chat_id: معرف القروب
            bot_username: اسم مستخدم البوت (بدون @)
        """
        try:
            await self.client.add_chat_members(
                chat_id=chat_id,
                user_ids=[f"@{bot_username}"]
            )
            logger.info(f"تم إضافة البوت @{bot_username} إلى القروب {chat_id}")
            return True
        except Exception as e:
            logger.error(f"فشل إضافة البوت: {e}")
            return False
    
    async def promote_to_admin(self, chat_id, user_id):
        """
        ترقية عضو إلى مدير
        
        Args:
            chat_id: معرف القروب
            user_id: معرف المستخدم
        """
        try:
            await self.client.promote_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                privileges={
                    'can_manage_chat': True,
                    'can_delete_messages': True,
                    'can_manage_video_chats': True,
                    'can_restrict_members': True,
                    'can_promote_members': False,
                    'can_change_info': True,
                    'can_invite_users': True,
                    'can_pin_messages': True
                }
            )
            logger.info(f"تم ترقية {user_id} إلى مدير في {chat_id}")
            return True
        except Exception as e:
            logger.error(f"فشل الترقية: {e}")
            return False
    
    async def start(self):
        """بدء الاتصال"""
        await self.client.start()
        logger.info("تم الاتصال بـ Telegram")
    
    async def stop(self):
        """إيقاف الاتصال"""
        await self.client.stop()
        logger.info("تم قطع الاتصال")


# ==================== Synchronous Wrapper ====================

def create_telegram_groups_sync(api_id, api_hash, phone_number, grade_name, sections, subject_name, school_name=None, teacher_name=None, bot_username=None):
    """
    دالة متزامنة لإنشاء قروبات تيليجرام
    
    Args:
        api_id: Telegram API ID
        api_hash: Telegram API Hash
        phone_number: رقم الهاتف
        grade_name: اسم الصف (مثال: "الصف الثالث متوسط")
        subject_name: اسم المادة (مثال: "المهارات الرقمية")
        sections: قائمة الشُعب (مثال: ["أ", "ب", "ج"])
        bot_username: اسم مستخدم البوت (اختياري)
        school_name: اسم المدرسة (اختياري)
    
    Returns:
        list: نتائج إنشاء القروبات
    """
    import asyncio
    
    async def _create():
        creator = TelegramGroupCreator(api_id, api_hash, phone_number)
        
        try:
            # بدء الاتصال
            await creator.start()
            
            # بناء قائمة القروبات
            groups_data = []
            for section in sections:
                group_name = f"{grade_name} {section} - {subject_name}"
                
                # رسالة ترحيبية احترافية
                description = (
                    f"🎓 مرحباً بكم في قروب {subject_name}\n\n"
                    f"📚 الصف: {grade_name} - الشعبة {section}\n"
                )
                if school_name:
                    description += f"🏫 المدرسة: {school_name}\n"
                description += (
                    "\n💎 منصتك الشاملة للتميز الأكاديمي\n"
                    "📢 إعلانات المشاريع | 📊 متابعة الإنجاز\n"
                    "📁 ملفات مساعدة | ⏰ تنبيهات ذكية\n\n"
                    "🌟 معاً نحو التميز والنجاح!"
                )
                
                groups_data.append({
                    'name': group_name,
                    'description': description,
                    'section': section
                })
            
            # إنشاء القروبات
            results = await creator.create_multiple_groups(groups_data, delay=5)
            
            # إضافة البوت إلى كل قروب (إذا كان موجود)
            if bot_username:
                for result in results:
                    if result.get('success') and result.get('chat_id'):
                        await creator.add_bot_to_group(
                            result['chat_id'],
                            bot_username
                        )
                        # ترقية البوت إلى مدير
                        await creator.promote_to_admin(
                            result['chat_id'],
                            bot_username
                        )
            
            return results
            
        finally:
            # إيقاف الاتصال
            await creator.stop()
    
    # تشغيل async function في thread منفصل
    import threading
    
    result = {'data': None, 'error': None}
    
    def run_async():
        try:
            # إنشاء event loop جديد لهذا الـ thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result['data'] = loop.run_until_complete(_create())
            loop.close()
        except Exception as e:
            result['error'] = e
    
    # تشغيل في thread منفصل
    thread = threading.Thread(target=run_async)
    thread.start()
    thread.join()  # انتظر حتى ينتهي
    
    if result['error']:
        raise result['error']
    
    return result['data']
