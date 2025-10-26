"""
Telegram Session Manager - Telethon Version
إدارة sessions باستخدام Telethon
"""
import os
from django.conf import settings
from telethon import TelegramClient, errors


class TelethonSessionManager:
    """إدارة sessions Telegram باستخدام Telethon"""
    
    def __init__(self):
        self.sessions_dir = os.path.join(settings.BASE_DIR, 'sessions')
        os.makedirs(self.sessions_dir, exist_ok=True)
        self._active_clients = {}  # {phone: (client, phone_code_hash)}
    
    def _get_session_path(self, phone_number):
        """الحصول على مسار session"""
        clean_phone = phone_number.replace('+', '').replace(' ', '')
        session_name = f"session_{clean_phone}"
        return os.path.join(self.sessions_dir, session_name)
    
    async def login_and_save_session(self, phone_number):
        """
        إرسال كود التحقق وحفظ client مؤقتاً
        """
        try:
            api_id = settings.TELEGRAM_API_ID
            api_hash = settings.TELEGRAM_API_HASH
            
            if not api_id or not api_hash:
                return {
                    'status': 'error',
                    'message': 'إعدادات Telegram API غير موجودة'
                }
            
            # مسار الجلسة
            session_path = self._get_session_path(phone_number)
            
            # إنشاء Client
            client = TelegramClient(session_path, int(api_id), api_hash)
            
            # الاتصال
            await client.connect()
            
            # التحقق من وجود جلسة
            if await client.is_user_authorized():
                await client.disconnect()
                return {
                    'status': 'already_connected',
                    'message': 'حسابك مربوط مسبقاً!'
                }
            
            # إرسال كود التحقق
            sent = await client.send_code_request(phone_number)
            
            # حفظ client مؤقتاً
            self._active_clients[phone_number] = (client, sent.phone_code_hash)
            
            return {
                'status': 'code_required',
                'phone_code_hash': sent.phone_code_hash,
                'message': 'أدخل كود التحقق المرسل إلى هاتفك'
            }
            
        except Exception as e:
            print(f"Error in login_and_save_session: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'خطأ: {str(e)}'
            }
    
    async def verify_code(self, phone_number, code, phone_code_hash):
        """
        التحقق من الكود وإكمال تسجيل الدخول
        """
        try:
            # الحصول على client المحفوظ
            if phone_number not in self._active_clients:
                return {
                    'status': 'error',
                    'message': 'انتهت صلاحية الجلسة. يرجى إعادة طلب الكود.'
                }
            
            client, saved_hash = self._active_clients[phone_number]
            
            # التحقق من الكود
            try:
                await client.sign_in(phone=phone_number, code=code, phone_code_hash=saved_hash)
                
                # نجح! الجلسة محفوظة تلقائياً
                await client.disconnect()
                
                # حذف من memory
                del self._active_clients[phone_number]
                
                return {
                    'status': 'success',
                    'message': 'تم ربط حسابك بنجاح!'
                }
                
            except errors.SessionPasswordNeededError:
                # يحتاج كلمة مرور 2FA
                return {
                    'status': 'password_required',
                    'message': 'الحساب محمي بالتحقق بخطوتين. يرجى إدخال كلمة المرور.'
                }
                
        except Exception as e:
            print(f"Error in verify_code: {e}")
            import traceback
            traceback.print_exc()
            
            # تنظيف
            if phone_number in self._active_clients:
                try:
                    await self._active_clients[phone_number][0].disconnect()
                except:
                    pass
                del self._active_clients[phone_number]
            
            return {
                'status': 'error',
                'message': f'خطأ في التحقق: {str(e)}'
            }
    
    async def verify_password(self, phone_number, password):
        """
        التحقق من كلمة المرور للحسابات المحمية بـ 2FA
        """
        try:
            if phone_number not in self._active_clients:
                return {
                    'status': 'error',
                    'message': 'انتهت صلاحية الجلسة. يرجى إعادة طلب الكود.'
                }
            
            client, _ = self._active_clients[phone_number]
            
            # التحقق من كلمة المرور
            await client.sign_in(password=password)
            
            # نجح!
            await client.disconnect()
            del self._active_clients[phone_number]
            
            return {
                'status': 'success',
                'message': 'تم ربط حسابك بنجاح!'
            }
            
        except errors.PasswordHashInvalidError:
            return {
                'status': 'error',
                'message': 'كلمة المرور غير صحيحة. حاول مرة أخرى.'
            }
        except Exception as e:
            print(f"Error in verify_password: {e}")
            
            # تنظيف
            if phone_number in self._active_clients:
                try:
                    await self._active_clients[phone_number][0].disconnect()
                except:
                    pass
                del self._active_clients[phone_number]
            
            return {
                'status': 'error',
                'message': f'خطأ في التحقق من كلمة المرور: {str(e)}'
            }
    
    def is_session_exists(self, phone_number):
        """التحقق من وجود session"""
        session_path = self._get_session_path(phone_number)
        return os.path.exists(f"{session_path}.session")
    
    def delete_session(self, phone_number):
        """حذف session"""
        session_path = self._get_session_path(phone_number)
        session_file = f"{session_path}.session"
        
        if os.path.exists(session_file):
            os.remove(session_file)
            # حذف journal file أيضاً
            journal_file = f"{session_path}.session-journal"
            if os.path.exists(journal_file):
                os.remove(journal_file)
            return True
        return False


# Singleton
telethon_session_manager = TelethonSessionManager()
