"""
Telegram Groups Auto-Creation
إنشاء قروبات تيليجرام تلقائياً
"""
import os
import asyncio
import logging
from typing import Dict, List, Optional
from telegram import Bot, ChatPermissions
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramGroupCreator:
    """
    مسؤول عن إنشاء قروبات تيليجرام تلقائياً
    """
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        self.bot = Bot(token=self.bot_token)
    
    async def create_group(
        self,
        group_name: str,
        description: str,
        rules: str,
        teacher_telegram_id: int,
        subject_name: str = None
    ) -> Dict:
        """
        إنشاء قروب تيليجرام واحد
        
        Args:
            group_name: اسم القروب (مثلاً: "الصف الثالث أ - المهارات الرقمية")
            description: وصف القروب
            rules: قوانين القروب
            teacher_telegram_id: معرف تيليجرام للمعلم
            subject_name: اسم المادة (اختياري)
        
        Returns:
            {
                'success': True/False,
                'chat_id': معرف القروب,
                'invite_link': رابط الدعوة,
                'group_name': اسم القروب,
                'error': رسالة الخطأ (إن وجد)
            }
        """
        try:
            logger.info(f"Creating Telegram group: {group_name}")
            
            # 1. إنشاء القروب (Supergroup)
            chat = await self.bot.create_chat(
                title=group_name,
                description=description
            )
            
            chat_id = chat.id
            logger.info(f"Group created with ID: {chat_id}")
            
            # 2. إضافة المعلم كعضو أولاً
            try:
                await self.bot.add_chat_member(
                    chat_id=chat_id,
                    user_id=teacher_telegram_id
                )
                logger.info(f"Teacher {teacher_telegram_id} added to group")
            except TelegramError as e:
                logger.warning(f"Could not add teacher: {e}")
            
            # 3. ترقية المعلم كمدير
            try:
                await self.bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=teacher_telegram_id,
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
                logger.info(f"Teacher promoted to admin")
            except TelegramError as e:
                logger.warning(f"Could not promote teacher: {e}")
            
            # 4. إنشاء رابط دعوة للقروب
            invite_link = await self.bot.export_chat_invite_link(chat_id)
            logger.info(f"Invite link created: {invite_link}")
            
            # 5. إضافة القوانين كرسالة مثبتة
            if rules:
                rules_message = f"📋 **قوانين القروب**\n\n{rules}"
                try:
                    message = await self.bot.send_message(
                        chat_id=chat_id,
                        text=rules_message,
                        parse_mode='Markdown'
                    )
                    await self.bot.pin_chat_message(
                        chat_id=chat_id,
                        message_id=message.message_id,
                        disable_notification=True
                    )
                    logger.info("Rules message pinned")
                except TelegramError as e:
                    logger.warning(f"Could not pin rules: {e}")
            
            # 6. تعيين أذونات افتراضية للأعضاء
            try:
                await self.bot.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_polls=False,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                        can_change_info=False,
                        can_invite_users=True,
                        can_pin_messages=False
                    )
                )
                logger.info("Chat permissions set")
            except TelegramError as e:
                logger.warning(f"Could not set permissions: {e}")
            
            return {
                'success': True,
                'chat_id': chat_id,
                'invite_link': invite_link,
                'group_name': group_name,
                'error': None
            }
            
        except TelegramError as e:
            logger.error(f"Failed to create group '{group_name}': {e}")
            return {
                'success': False,
                'chat_id': None,
                'invite_link': None,
                'group_name': group_name,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error creating group '{group_name}': {e}")
            return {
                'success': False,
                'chat_id': None,
                'invite_link': None,
                'group_name': group_name,
                'error': f"خطأ غير متوقع: {str(e)}"
            }
    
    async def create_multiple_groups(
        self,
        grade_name: str,
        subject_name: str,
        sections: List[str],
        teacher_telegram_id: int,
        school_name: str = None,
        delay_seconds: int = 3
    ) -> List[Dict]:
        """
        إنشاء عدة قروبات دفعة واحدة
        
        Args:
            grade_name: اسم الصف (مثل: "الصف الثالث")
            subject_name: اسم المادة (مثل: "المهارات الرقمية")
            sections: قائمة الشُعب ["أ", "ب", "ج"]
            teacher_telegram_id: معرف تيليجرام للمعلم
            school_name: اسم المدرسة (اختياري)
            delay_seconds: التأخير بين كل قروب (لتجنب Rate Limiting)
        
        Returns:
            قائمة بنتائج إنشاء كل قروب
        """
        results = []
        
        # الوصف والقوانين الافتراضية
        description = self._generate_description(grade_name, subject_name, school_name)
        rules = self._generate_rules(subject_name)
        
        for i, section_name in enumerate(sections):
            # اسم القروب بالنمط المطلوب: "الصف الثالث أ - المهارات الرقمية"
            group_name = f"{grade_name} {section_name} - {subject_name}"
            
            # إنشاء القروب
            result = await self.create_group(
                group_name=group_name,
                description=description,
                rules=rules,
                teacher_telegram_id=teacher_telegram_id,
                subject_name=subject_name
            )
            
            result['section_name'] = section_name
            results.append(result)
            
            logger.info(f"Group {i+1}/{len(sections)} created: {result['success']}")
            
            # تأخير بين الطلبات (لتجنب Telegram Rate Limiting)
            if i < len(sections) - 1:  # لا نؤخر بعد آخر قروب
                await asyncio.sleep(delay_seconds)
        
        return results
    
    def _generate_description(
        self,
        grade_name: str,
        subject_name: str,
        school_name: Optional[str] = None
    ) -> str:
        """توليد وصف القروب"""
        desc = f"🎓 قروب {grade_name} - مادة {subject_name}\n\n"
        
        if school_name:
            desc += f"🏫 {school_name}\n\n"
        
        desc += (
            "📚 هذا القروب مخصص لـ:\n"
            "• تسليم المشاريع والواجبات\n"
            "• الإعلانات والتحديثات المهمة\n"
            "• التواصل مع المعلم\n\n"
            "⚡ يُرجى الالتزام بقوانين القروب"
        )
        
        return desc
    
    def _generate_rules(self, subject_name: str, teacher_name: str = None) -> str:
        """توليد رسالة الترحيب والإرشادات - النسخة العصرية"""
        rules = (
            "╔══════════════════════╗\n"
            "║  🎓 مرحباً بكم! 🎓  ║\n"
            "╚══════════════════════╝\n\n"
            
            f"📚 **المادة:** {subject_name}\n"
            "🏫 **الصف:** [يتم التحديث تلقائياً]\n"  
            f"👨‍🏫 **المعلم:** {teacher_name or '[يتم التحديث تلقائياً]'}\n\n"
            
            "─────────────────────\n\n"
            
            "💎 **منصتك الشاملة للتميز الأكاديمي**\n\n"
            
            "🎯 **المشاريع:**\n"
            "   📢 إعلانات فورية\n"
            "   📝 تعليمات واضحة\n"
            "   🔗 روابط التسليم\n\n"
            
            "📈 **التتبع الذكي:**\n"
            "   ✅ إحصائيات دقيقة\n"
            "   📊 متابعة الإنجاز\n"
            "   🏆 نتائج وتقييمات\n\n"
            
            "📚 **المحتوى التعليمي:**\n"
            "   🎥 فيديوهات شرح\n"
            "   📄 ملفات PDF\n"
            "   🔗 مراجع ومصادر\n"
            "   💡 نماذج وأمثلة\n\n"
            
            "⏰ **التنبيهات الذكية:**\n"
            "   🔔 تذكير بالمواعيد\n"
            "   ⚡ إشعارات فورية\n"
            "   ⏳ تحذير قبل الانتهاء\n\n"
            
            "─────────────────────\n\n"
            
            "⚠️ **إرشادات القروب:**\n"
            "✓ القروب للقراءة فقط (Read-Only)\n"
            "✓ فعّل الإشعارات للبقاء على اطلاع\n"
            "✓ للاستفسارات: تواصل مع المعلم\n\n"
            
            "─────────────────────\n\n"
            
            "🌟 معاً نحو التميز والنجاح! 🌟\n\n"
            
            "─────────────────────\n"
            "🤖 Powered by SmartEdu"
        )
        
        return rules


def create_telegram_groups_sync(
    grade_name: str,
    subject_name: str,
    sections: List[str],
    teacher_telegram_id: int,
    school_name: str = None
) -> List[Dict]:
    """
    نسخة Synchronous لإنشاء القروبات (للاستخدام مع Django Views)
    """
    creator = TelegramGroupCreator()
    
    # تشغيل الـ async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(
            creator.create_multiple_groups(
                grade_name=grade_name,
                subject_name=subject_name,
                sections=sections,
                teacher_telegram_id=teacher_telegram_id,
                school_name=school_name
            )
        )
        return results
    finally:
        loop.close()
