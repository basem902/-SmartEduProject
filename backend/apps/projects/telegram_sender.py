"""
Telegram Sender with WebSocket Progress Updates
"""
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .telegram_helper import TelegramProjectNotifier
from .models import TelegramSendLog


async def send_project_with_progress(project, room_group_name, section_ids=None):
    """Send project to telegram with real-time progress updates"""
    channel_layer = get_channel_layer()
    
    async def send_update(message_type, message, data=None):
        """Helper to send WebSocket update"""
        await channel_layer.group_send(
            room_group_name,
            {
                'type': 'send_progress',
                'data': {
                    'type': message_type,
                    'message': message,
                    'data': data or {}
                }
            }
        )
    
    try:
        # Get sections
        if section_ids:
            sections = await asyncio.to_thread(
                lambda: list(project.sections.filter(id__in=section_ids))
            )
        else:
            sections = await asyncio.to_thread(
                lambda: list(project.sections.all())
            )
        
        total = len(sections)
        
        await send_update('info', f'📊 عدد الشُعب: {total}')
        await send_update('progress', f'0/{total}', {'current': 0, 'total': total})
        
        # Create notifier
        notifier = TelegramProjectNotifier()
        
        # Check token
        if not notifier.bot_token:
            await send_update('error', '❌ TELEGRAM_BOT_TOKEN غير موجود!')
            return
        
        await send_update('success', '✅ Bot Token موجود')
        
        success_count = 0
        failed_count = 0
        
        # Process each section
        for index, section in enumerate(sections, 1):
            section_name = section.section_name
            
            await send_update('info', f'🔄 معالجة الشعبة: {section_name} (ID: {section.id})')
            
            try:
                # Get chat_id
                await send_update('info', '   📱 الحصول على chat_id...')
                chat_id = await asyncio.to_thread(notifier._get_chat_id_from_section, section)
                
                if not chat_id:
                    raise Exception('لا يوجد chat_id')
                
                await send_update('success', f'   ✅ chat_id: {chat_id}')
                
                # Generate link
                await send_update('info', '   🔗 توليد رابط التسليم...')
                submission_link = await asyncio.to_thread(
                    notifier._generate_submission_link, project, section
                )
                await send_update('success', f'   ✅ {submission_link[:50]}...')
                
                # Format message
                await send_update('info', '   📝 تنسيق الرسالة...')
                message = await asyncio.to_thread(
                    notifier._format_project_message, project, section, submission_link
                )
                keyboard = await asyncio.to_thread(
                    notifier._create_inline_keyboard, submission_link, project
                )
                
                # Send message
                await send_update('info', f'   📤 إرسال إلى chat_id: {chat_id}')
                sent_msg = await asyncio.to_thread(
                    notifier._send_message_with_keyboard, chat_id, message, keyboard
                )
                
                if not sent_msg:
                    raise Exception('فشل الإرسال')
                
                message_id = sent_msg.get('message_id')
                await send_update('success', f'   ✅ نجح الإرسال! message_id: {message_id}')
                
                success_count += 1
                
                # Save log
                await save_send_log(project, section, True, f'message_id: {message_id}')
                
            except Exception as e:
                error_msg = str(e)
                await send_update('error', f'   ❌ فشل: {error_msg}')
                failed_count += 1
                
                # Save error log
                await save_send_log(project, section, False, error_msg)
            
            # Update progress
            await send_update('progress', f'{index}/{total}', {
                'current': index,
                'total': total,
                'success': success_count,
                'failed': failed_count
            })
            
            # Small delay between sections
            await asyncio.sleep(0.5)
        
        # Final summary
        await send_update('summary', '📊 النتيجة النهائية:', {
            'success': success_count,
            'failed': failed_count,
            'total': total
        })
        
        if failed_count == 0:
            await send_update('complete', '🎉 تم الإرسال بنجاح لجميع الشُعب!')
        else:
            await send_update('complete', f'⚠️ اكتمل الإرسال: {success_count} نجح، {failed_count} فشل')
        
    except Exception as e:
        await send_update('error', f'❌ خطأ عام: {str(e)}')


async def save_send_log(project, section, success, details):
    """Save send log to database"""
    await asyncio.to_thread(
        TelegramSendLog.objects.create,
        project=project,
        section=section,
        success=success,
        details=details
    )
