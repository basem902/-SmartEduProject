"""
Telegram Integration Helper for Projects - Enhanced Version
"""
import logging
import requests
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
import html
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class TelegramProjectNotifier:
    """Handle sending project notifications to Telegram"""
    
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
        self.bot_info = None  # Will be set after verification
    
    def verify_bot_token(self):
        """Verify bot token is valid by calling getMe"""
        if not self.bot_token or not self.api_url:
            return False
        
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=5)
            result = response.json()
            
            if result.get('ok'):
                self.bot_info = result.get('result')
                print(f"   ✅ Bot Token صحيح")
                print(f"      🤖 Bot Username: @{self.bot_info.get('username')}")
                print(f"      📛 Bot Name: {self.bot_info.get('first_name')}")
                return True
            else:
                print(f"   ❌ Bot Token غير صحيح!")
                print(f"      Error: {result.get('description')}")
                logger.error(f"Invalid bot token: {result.get('description')}")
                return False
        except Exception as e:
            print(f"   ❌ فشل التحقق من Bot Token: {str(e)}")
            logger.error(f"Failed to verify bot token: {str(e)}")
            return False
    
    def check_bot_in_chat(self, chat_id):
        """Check if bot is member of the chat"""
        if not self.api_url:
            return False
        
        try:
            url = f"{self.api_url}/getChatMember"
            data = {
                'chat_id': chat_id,
                'user_id': self.bot_info.get('id') if self.bot_info else None
            }
            
            if not data['user_id']:
                print("      ⚠️ Bot info not available, skipping membership check")
                return True  # Skip check if bot info not available
            
            response = requests.post(url, json=data, timeout=5)
            result = response.json()
            
            if result.get('ok'):
                member = result.get('result', {})
                status = member.get('status')
                print(f"      👤 Bot Status في المجموعة: {status}")
                
                # Bot should be member or admin to send messages
                if status in ['member', 'administrator', 'creator']:
                    return True
                else:
                    print(f"      ⚠️ Bot ليس عضو في المجموعة (Status: {status})")
                    return False
            else:
                error_desc = result.get('description', 'Unknown')
                print(f"      ⚠️ فشل التحقق من عضوية البوت: {error_desc}")
                # If we can't check, assume it's ok (might be a permissions issue)
                return True
        except Exception as e:
            print(f"      ⚠️ خطأ في التحقق من عضوية البوت: {str(e)}")
            # If check fails, assume it's ok to try sending
            return True
    
    def send_project_notification(self, project, send_files=True, pin_message=False):
        """
        Send project notification to all sections with enhanced features
        Returns: dict with success/failed lists and statistics
        """
        print("\n" + "=" * 60)
        print(f"📡 بدء إرسال إشعار المشروع: {project.title}")
        print(f"   - Project ID: {project.id}")
        print(f"   - Bot Token: {'✅ موجود' if self.bot_token else '❌ مفقود'}")
        print("=" * 60 + "\n")
        
        if not self.bot_token:
            logger.warning("Telegram bot token not configured")
            print("❌ خطأ: TELEGRAM_BOT_TOKEN غير موجود!")
            return {
                'success': [],
                'failed': [],
                'total': 0,
                'success_count': 0,
                'failed_count': 0
            }
        
        # Verify bot token before sending
        print("🔍 التحقق من صحة Bot Token...")
        if not self.verify_bot_token():
            print("❌ فشل التحقق من Bot Token! لن يتم إرسال الرسائل.")
            return {
                'success': [],
                'failed': [],
                'total': 0,
                'success_count': 0,
                'failed_count': 0
            }
        print()
        
        results = {
            'success': [],
            'failed': [],
            'total': 0,
            'success_count': 0,
            'failed_count': 0
        }
        
        sections = project.sections.all()
        results['total'] = sections.count()
        
        print(f"📊 عدد الشُعب: {sections.count()}")
        print("-" * 60 + "\n")
        
        for section in sections:
            print(f"\n🔄 معالجة الشعبة: {section.section_name} (ID: {section.id})")
            try:
                # Get chat ID from TelegramGroup model
                print("   📱 محاولة الحصول على chat_id...")
                chat_id = self._get_chat_id_from_section(section)
                
                if not chat_id:
                    error_msg = f"❌ فشل: لا يوجد chat_id للشعبة {section.section_name}"
                    print(f"   {error_msg}")
                    logger.warning(f"No chat ID for section {section.id}")
                    results['failed'].append({
                        'section_id': section.id,
                        'section_name': section.section_name,
                        'error': 'No Telegram group found',
                        'students_count': getattr(section, 'registrations_count', 0)
                    })
                    results['failed_count'] += 1
                    continue
                
                print(f"   ✅ chat_id: {chat_id}")
                
                # Check if bot is in the group
                print("   🔍 التحقق من عضوية البوت في المجموعة...")
                if not self.check_bot_in_chat(chat_id):
                    error_msg = "البوت ليس عضواً في المجموعة"
                    print(f"   ❌ فشل: {error_msg}")
                    results['failed'].append({
                        'section_id': section.id,
                        'section_name': section.section_name,
                        'error': error_msg,
                        'students_count': getattr(section, 'registrations_count', 0)
                    })
                    results['failed_count'] += 1
                    continue
                
                # Generate submission link with JWT
                print("   🔗 توليد رابط التسليم...")
                submission_link = self._generate_submission_link(project, section)
                print(f"   ✅ رابط التسليم: {submission_link[:50]}...")
                
                # Format message with inline keyboard
                print("   📝 تنسيق الرسالة...")
                message = self._format_project_message(project, section, submission_link)
                keyboard = self._create_inline_keyboard(submission_link, project)
                
                # Send message
                print(f"   📤 إرسال الرسالة إلى chat_id: {chat_id}")
                sent_msg = self._send_message_with_keyboard(chat_id, message, keyboard)
                
                if not sent_msg:
                    print("   ❌ فشل: لم يتم إرسال الرسالة (sent_msg = None)")
                    raise Exception('Failed to send message')
                
                print(f"   ✅ نجح الإرسال! message_id: {sent_msg.get('message_id')}")
                
                # Pin message if requested
                if pin_message and sent_msg.get('message_id'):
                    self._pin_message(chat_id, sent_msg['message_id'])
                
                # Send files if requested
                if send_files:
                    self._send_project_files(chat_id, project)
                
                results['success'].append({
                    'section_id': section.id,
                    'section_name': section.section_name,
                    'students_count': getattr(section, 'registrations_count', 0),
                    'message_id': sent_msg.get('message_id')
                })
                results['success_count'] += 1
                print(f"   🎉 تم بنجاح للشعبة {section.section_name}")
                logger.info(f"✅ Sent notification to section {section.section_name}")
                
            except Exception as e:
                error_detail = str(e)
                print(f"   ❌ فشل الإرسال للشعبة {section.section_name}")
                print(f"   🔍 السبب: {error_detail}")
                logger.error(f"❌ Failed to send to section {section.id}: {error_detail}")
                results['failed'].append({
                    'section_id': section.id,
                    'section_name': section.section_name,
                    'error': error_detail,
                    'students_count': getattr(section, 'registrations_count', 0)
                })
                results['failed_count'] += 1
        
        print("\n" + "=" * 60)
        print("📊 النتيجة النهائية:")
        print(f"   ✅ نجح: {results['success_count']}")
        print(f"   ❌ فشل: {results['failed_count']}")
        print(f"   📊 المجموع: {results['total']}")
        print("=" * 60 + "\n")
        
        return results
    
    def _get_chat_id_from_section(self, section):
        """Get chat ID from section's TelegramGroup model"""
        from apps.sections.models import TelegramGroup
        
        try:
            # Try to get from TelegramGroup model (primary method)
            try:
                telegram_group = TelegramGroup.objects.get(section=section)
                if telegram_group and telegram_group.chat_id:
                    raw_cid = telegram_group.chat_id
                    cid = self._normalize_chat_id(raw_cid)
                    if str(cid) != str(raw_cid):
                        logger.info(f"🔧 Normalized chat_id for section {section.id} from {raw_cid} to {cid}")
                    logger.info(f"✅ Found chat_id for section {section.id} ({section.section_name}): {cid}")
                    return cid
                else:
                    logger.warning(f"⚠️ Section {section.id} ({section.section_name}) has telegram_group but no chat_id")
                    return None
            except TelegramGroup.DoesNotExist:
                logger.warning(f"⚠️ Section {section.id} ({section.section_name}) has NO telegram group created yet")
                return None
            
            # Fallback: try from SectionLink model
            if hasattr(section, 'link') and section.link:
                if hasattr(section.link, 'chat_id') and section.link.chat_id:
                    raw_cid = section.link.chat_id
                    cid = self._normalize_chat_id(raw_cid)
                    if str(cid) != str(raw_cid):
                        logger.info(f"🔧 Normalized link chat_id for section {section.id} from {raw_cid} to {cid}")
                    logger.info(f"✅ Found chat_id from link for section {section.id}")
                    return cid
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting chat ID for section {section.id}: {str(e)}", exc_info=True)
            return None

    def _normalize_chat_id(self, chat_id):
        """Ensure Telegram chat_id is negative with -100 prefix for groups/supergroups."""
        try:
            if chat_id is None:
                return None
            cid = int(chat_id)
            # already negative
            if cid < 0:
                # if already has -100 prefix, keep
                if str(cid).startswith('-100'):
                    return cid
                # attempt to fix old 1e11-based normalization (e.g., -1032...)
                abs_cid = abs(cid)
                if 100000000000 <= abs_cid < 1000000000000:
                    # revert to positive id then convert to -100 prefix
                    positive_id = abs_cid - 100000000000
                    return -(1000000000000 + positive_id)
                return cid
            # positive -> convert to -100 prefix form (1e12)
            return -(1000000000000 + cid)
        except Exception:
            return chat_id
    
    def _generate_submission_link(self, project, section):
        """Generate secure submission link with JWT token"""
        try:
            # Create JWT token
            payload = {
                'project_id': project.id,
                'section_id': section.id,
                'exp': int(project.deadline.timestamp()),
                'iat': int(datetime.now().timestamp())
            }
            
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            
            # Return full URL
            return f"{self.frontend_url}/pages/submit-project.html?token={token}"
            
        except Exception as e:
            logger.error(f"Error generating submission link: {str(e)}")
            # Fallback to simple link
            return f"{self.frontend_url}/pages/submit-project.html?project_id={project.id}"
    
    def _create_inline_keyboard(self, submission_link, project):
        """Create inline keyboard with buttons (only if URLs valid for Telegram)"""
        rows = []
        
        # Primary submit button: only if URL is https and not localhost
        if self._is_valid_button_url(submission_link):
            rows.append([
                {
                    'text': '🚀 تسليم المشروع الآن',
                    'url': submission_link
                }
            ])
        
        # Additional buttons row
        buttons_row = []
        video_link = self._get_video_link(project)
        if video_link and self._is_valid_button_url(video_link):
            buttons_row.append({'text': '📹 فيديو الشرح', 'url': video_link})
        if self._has_external_links(project):
            # Generic callback button (requires bot callback handler if used later)
            buttons_row.append({'text': '🔗 روابط مفيدة', 'callback_data': f'links_{project.id}'})
        if buttons_row:
            rows.append(buttons_row)
        
        return {'inline_keyboard': rows} if rows else None
    
    def _format_project_message(self, project, section, submission_link):
        """Format professional project notification message"""
        
        # Calculate days remaining
        days_remaining = (project.deadline - timezone.now()).days
        
        # Status icon based on days remaining
        status_icon = '🟢' if days_remaining > 7 else '🟡' if days_remaining > 3 else '🔴'
        
        # Format dates in Arabic
        start_date = project.start_date.strftime('%d %B %Y - %I:%M %p')
        deadline = project.deadline.strftime('%d %B %Y - %I:%M %p')
        
        # Format file types
        if project.allowed_file_types:
            file_types = ' • '.join([f"<code>{html.escape(str(ft))}</code>" for ft in project.allowed_file_types])
        else:
            file_types = 'جميع الأنواع'
        
        # Build message with HTML formatting
        message = f"""
📚 ━━━━━━ <b>مشروع جديد</b> ━━━━━━ 📚

📌 <b>العنوان:</b> {self._escape_html(project.title)}
📖 <b>المادة:</b> {self._escape_html(project.subject)}
🏫 <b>الشعبة:</b> {self._escape_html(section.section_name)}
👨‍🏫 <b>المعلم:</b> {self._escape_html(project.teacher.full_name)}

━━━━━━━━━━━━━━━━━━━━━━

📝 <b>الوصف:</b>
{self._escape_html(project.description) if project.description else 'لا يوجد وصف'}

━━━━━━━━━━━━━━━━━━━━━━

📋 <b>التعليمات:</b>
{self._format_text_with_bullets(project.instructions)}

━━━━━━━━━━━━━━━━━━━━━━

⚠️ <b>الشروط:</b>
{self._format_text_with_bullets(project.requirements)}
"""

        # Add tips if available
        if project.tips:
            message += f"""
━━━━━━━━━━━━━━━━━━━━━━

💡 <b>نصائح للطلاب:</b>
{self._format_text_with_bullets(project.tips)}
"""

        # Add submission requirements
        message += f"""
━━━━━━━━━━━━━━━━━━━━━━

📅 <b>المواعيد:</b>
🟢 البداية: {start_date}
{status_icon} النهاية: {deadline}
⏰ المتبقي: <b>{days_remaining} يوم</b>

🎯 <b>الدرجة الكاملة:</b> {project.max_grade} درجة

━━━━━━━━━━━━━━━━━━━━━━

📎 <b>متطلبات التسليم:</b>
• الملفات المسموحة: {file_types}
• الحد الأقصى: <b>{project.max_file_size} MB</b>
• التسليم المتأخر: {'✅ مسموح' if project.allow_late_submission else '❌ غير مسموح'}

━━━━━━━━━━━━━━━━━━━━━━

⚡ <b>اضغط الزر بالأسفل للتسليم</b>
⚠️ تأكد من قراءة جميع التعليمات قبل التسليم

🔗 رابط التسليم:
{self._escape_html(submission_link)}
"""
        
        return message.strip()
    
    def _format_text_with_bullets(self, text):
        """Format text with proper bullet points"""
        if not text:
            return 'لا يوجد'
        
        lines = text.strip().split('\n')
        formatted = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                content = line[1:].strip() if (line.startswith('•') or line.startswith('-')) else line
                formatted.append(f"{i}️⃣ {self._escape_html(content)}")
        
        return '\n'.join(formatted) if formatted else text
    
    def _escape_html(self, text):
        """Escape HTML entities for Telegram HTML parse mode"""
        if text is None:
            return ''
        try:
            return html.escape(str(text), quote=False)
        except Exception:
            return str(text)
    
    def _get_video_link(self, project):
        """Extract a video external link from related ProjectFile records, if any"""
        try:
            files = project.files.all()
            # Priority 1: video file_type with external_link (e.g., YouTube/Vimeo/Drive)
            for pf in files:
                if getattr(pf, 'file_type', '') == 'video' and getattr(pf, 'external_link', None):
                    return pf.external_link
            # Priority 2: generic link that looks like a video URL
            for pf in files:
                url = getattr(pf, 'external_link', '') or ''
                if any(x in url for x in ['youtube.com', 'youtu.be', 'vimeo.com']):
                    return url
        except Exception as e:
            logger.error(f"_get_video_link error: {str(e)}", exc_info=True)
        return None
    
    def _has_external_links(self, project):
        """Check if project has any non-video external links"""
        try:
            for pf in project.files.all():
                url = getattr(pf, 'external_link', None)
                if url and getattr(pf, 'file_type', '') != 'video':
                    return True
        except Exception as e:
            logger.error(f"_has_external_links error: {str(e)}", exc_info=True)
        return False
    
    def _send_message(self, chat_id, text):
        """Send text message to chat"""
        if not self.api_url:
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data, timeout=10)
            return response.json().get('ok', False)
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def _send_message_with_keyboard(self, chat_id, text, keyboard):
        """Send message with inline keyboard"""
        if not self.api_url:
            print("      ❌ فشل: api_url غير موجود (bot token مفقود)")
            logger.error("Cannot send message: api_url is None (bot token missing)")
            return None
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
            }
            if keyboard and keyboard.get('inline_keyboard'):
                data['reply_markup'] = keyboard
            
            # Log request details
            print(f"      📤 إرسال الطلب إلى: {url}")
            print(f"      📍 chat_id: {chat_id}")
            print(f"      ⚙️ keyboard: {'موجودة' if keyboard else 'غير موجودة'}")
            
            response = requests.post(url, json=data, timeout=10)
            
            # Log response status
            print(f"      📊 HTTP Status: {response.status_code}")
            
            # Check HTTP status first
            if response.status_code != 200:
                print(f"      ❌ HTTP Error: {response.status_code}")
                print(f"      📄 Response: {response.text[:200]}")
                logger.error(f"Telegram API HTTP error {response.status_code}: {response.text[:500]}")
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")
            
            result = response.json()
            
            # Log full response for debugging
            print(f"      📦 Response OK: {result.get('ok')}")
            if result.get('result'):
                msg_id = result['result'].get('message_id', 'N/A')
                chat = result['result'].get('chat', {})
                chat_title = chat.get('title', 'N/A')
                print(f"      ✅ message_id: {msg_id}")
                print(f"      💬 chat_title: {chat_title}")
            
            if result.get('ok'):
                return result.get('result')
            else:
                error_desc = result.get('description', 'Unknown error')
                error_code = result.get('error_code', 'N/A')
                print(f"      ⚠️ Telegram API Error:")
                print(f"         Code: {error_code}")
                print(f"         Description: {error_desc}")
                logger.error(f"Telegram API error ({error_code}): {error_desc}")
                raise Exception(f"Telegram API error ({error_code}): {error_desc}")
            
        except requests.exceptions.RequestException as e:
            print(f"      ❌ Network Error: {str(e)}")
            logger.error(f"Network error sending message: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
            logger.error(f"Error sending message with keyboard: {str(e)}")
            # Propagate the exception so upper layers can report detailed error
            raise

    def _is_valid_button_url(self, url: str) -> bool:
        """Validate URLs for Telegram button (must be https and not localhost)."""
        try:
            parsed = urlparse(url)
            if parsed.scheme != 'https':
                return False
            host = (parsed.hostname or '').lower()
            if host in ('localhost', '127.0.0.1'):
                return False
            return True
        except Exception:
            return False
    
    def _pin_message(self, chat_id, message_id):
        """Pin message in chat"""
        if not self.api_url:
            return False
        
        try:
            url = f"{self.api_url}/pinChatMessage"
            data = {
                'chat_id': chat_id,
                'message_id': message_id,
                'disable_notification': False
            }
            
            response = requests.post(url, json=data, timeout=10)
            return response.json().get('ok', False)
            
        except Exception as e:
            logger.error(f"Error pinning message: {str(e)}")
            return False
    
    def _send_project_files(self, chat_id, project):
        """Send project files to chat"""
        if not self.api_url:
            return
        
        try:
            files = project.files.all()
            logger.info(f"📎 Sending {files.count()} files to chat {chat_id}")
            
            for file in files:
                if file.file_type == 'link':
                    # Send as text message - use external_link or file_path as fallback
                    link_url = file.external_link or file.file_path
                    if link_url:
                        # Detect link type
                        if 'youtube.com' in link_url or 'youtu.be' in link_url:
                            link_label = '📺 فيديو يوتيوب'
                        elif 'drive.google.com' in link_url:
                            link_label = '📁 Google Drive'
                        else:
                            link_label = '🔗 رابط مفيد'
                        
                        link_text = f"{link_label}:\n{link_url}"
                        self._send_message(chat_id, link_text)
                        logger.info(f"✅ Sent link: {link_url}")
                    else:
                        logger.warning(f"⚠️ Link file has no URL: {file.id}")
                    
                elif file.file_path:
                    # Send file
                    self._send_file(chat_id, file)
                    
        except Exception as e:
            logger.error(f"❌ Error sending files: {str(e)}", exc_info=True)
    
    def _send_file(self, chat_id, project_file):
        """Send a single file to chat"""
        if not self.api_url:
            return False
        
        try:
            import os
            from django.conf import settings
            
            file_path = os.path.join(settings.MEDIA_ROOT, project_file.file_path)
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return False
            
            # Determine endpoint based on file type
            if project_file.file_type == 'video':
                endpoint = 'sendVideo'
            elif project_file.file_type == 'pdf':
                endpoint = 'sendDocument'
            else:
                endpoint = 'sendDocument'
            
            url = f"{self.api_url}/{endpoint}"
            
            with open(file_path, 'rb') as f:
                files = {'document': f} if endpoint == 'sendDocument' else {'video': f}
                data = {
                    'chat_id': chat_id,
                    'caption': project_file.file_name
                }
                
                response = requests.post(url, data=data, files=files, timeout=30)
                return response.json().get('ok', False)
                
        except Exception as e:
            logger.error(f"Error sending file {project_file.file_name}: {str(e)}")
            return False
    
    def send_reminder(self, project, hours_before=24):
        """Send reminder before deadline"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not project.send_reminder:
            return (0, 0)
        
        # Check if we should send reminder
        now = timezone.now()
        deadline = project.deadline
        time_until_deadline = deadline - now
        
        if time_until_deadline.total_seconds() / 3600 > hours_before:
            return (0, 0)  # Too early
        
        success = 0
        failed = 0
        
        for section in project.sections.all():
            try:
                chat_id = self._get_chat_id_from_section(section)
                if not chat_id:
                    failed += 1
                    continue
                
                reminder_message = f"""
⚠️ تذكير: اقتراب موعد التسليم

📌 المشروع: {project.title}
⏰ الموعد النهائي: {deadline.strftime('%Y-%m-%d %H:%M')}
⏳ المتبقي: {int(time_until_deadline.total_seconds() / 3600)} ساعة

🚀 رابط التسليم:
{self.frontend_url}/pages/submit-project.html?project_id={project.id}

⚡ لا تنسَ التسليم قبل انتهاء الوقت!
"""
                
                self._send_message(chat_id, reminder_message)
                success += 1
                
            except Exception as e:
                logger.error(f"Failed to send reminder to section {section.id}: {str(e)}")
                failed += 1
        
        return (success, failed)


# Singleton instance
telegram_notifier = TelegramProjectNotifier()
