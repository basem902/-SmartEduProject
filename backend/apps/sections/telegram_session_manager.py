"""
Telegram Session Manager
يدير sessions المستخدمين بشكل آمن ومشفر
"""
import os
import json
import base64
from cryptography.fernet import Fernet
from django.conf import settings

import asyncio

# تأجيل استيراد Pyrogram لتجنب مشاكل Event Loop
PYROGRAM_AVAILABLE = False
Client = None

def _import_pyrogram():
    """استيراد Pyrogram عند الحاجة فقط"""
    global PYROGRAM_AVAILABLE, Client
    if not PYROGRAM_AVAILABLE:
        try:
            from pyrogram import Client as PyrogramClient
            Client = PyrogramClient
            PYROGRAM_AVAILABLE = True
        except ImportError:
            print("Warning: Pyrogram not installed. Install it with: pip install pyrogram")
    return PYROGRAM_AVAILABLE


class TelegramSessionManager:
    """إدارة sessions تيليجرام بشكل آمن"""
    
    def __init__(self):
        # مفتاح التشفير (يجب أن يكون في settings.py)
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.sessions_dir = os.path.join(settings.BASE_DIR, 'sessions')
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # حفظ clients النشطة مع event loops الخاصة بها
        self._active_clients = {}  # {phone: client}
        self._client_loops = {}    # {phone: loop}
    
    def _get_encryption_key(self):
        """الحصول على مفتاح التشفير أو إنشاء واحد جديد"""
        key_file = os.path.join(settings.BASE_DIR, '.session_key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # إنشاء مفتاح جديد
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _get_session_path(self, phone_number):
        """الحصول على مسار session"""
        clean_phone = phone_number.replace('+', '').replace(' ', '')
        return os.path.join(self.sessions_dir, f"user_{clean_phone}")
    
    async def login_and_save_session(self, phone_number, code_callback=None):
        """
        تسجيل الدخول وحفظ session
        
        Args:
            phone_number: رقم الهاتف
            code_callback: دالة لإرسال كود التحقق للمستخدم
            
        Returns:
            dict: نتيجة العملية
        """
        # استيراد Pyrogram عند الحاجة
        if not _import_pyrogram():
            return {
                'status': 'error',
                'message': 'Pyrogram غير مثبت. قم بتثبيته: pip install pyrogram'
            }
        
        session_name = self._get_session_path(phone_number)
        
        try:
            # قراءة API credentials
            api_id = settings.TELEGRAM_API_ID
            api_hash = settings.TELEGRAM_API_HASH
            
            # Debug: طباعة القيم
            print(f"DEBUG: TELEGRAM_API_ID = {api_id} (type: {type(api_id).__name__})")
            print(f"DEBUG: TELEGRAM_API_HASH = {api_hash} (type: {type(api_hash).__name__})")
            
            # التحقق من القيم
            if not api_id or not api_hash:
                return {
                    'status': 'error',
                    'message': f'TELEGRAM_API_ID or TELEGRAM_API_HASH not configured. API_ID={api_id}, API_HASH={api_hash}'
                }
            
            # تحويل إلى int
            try:
                api_id = int(api_id)
            except (ValueError, TypeError) as e:
                return {
                    'status': 'error',
                    'message': f'TELEGRAM_API_ID is not a valid integer: {api_id} (type: {type(api_id).__name__})'
                }
            
            print(f"DEBUG: api_id after conversion = {api_id} (type: {type(api_id).__name__})")
            print(f"DEBUG: api_hash = {api_hash} (type: {type(api_hash).__name__})")
            
            # التحقق من وجود client نشط
            if phone_number in self._active_clients:
                print(f"WARNING: Active client already exists for {phone_number}")
                print(f"WARNING: Cleaning up old client...")
                try:
                    old_client = self._active_clients[phone_number]
                    await old_client.disconnect()
                except:
                    pass
                del self._active_clients[phone_number]
                print(f"DEBUG: Old client cleaned up")
            
            # استخدام in_memory لتجنب database lock تماماً
            clean_phone = phone_number.replace('+', '').replace(' ', '')
            session_name = f"session_{clean_phone}"
            
            print(f"DEBUG: Creating Client with session_name='{session_name}'")
            
            try:
                # استخدام workdir ثابت بناءً على رقم الهاتف
                import tempfile
                import os
                
                # إنشاء مجلد temp ثابت لهذا الرقم
                base_temp_dir = tempfile.gettempdir()
                phone_temp_dir = os.path.join(base_temp_dir, f"telegram_{clean_phone}")
                os.makedirs(phone_temp_dir, exist_ok=True)
                
                client = Client(
                    name=session_name,
                    api_id=api_id,
                    api_hash=api_hash,
                    workdir=phone_temp_dir
                )
                print(f"DEBUG: Client created successfully with workdir={phone_temp_dir}")
            except Exception as e:
                print(f"ERROR: Failed to create Client: {e}")
                print(f"ERROR: Type of error: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                return {
                    'status': 'error',
                    'message': f'Failed to create Pyrogram Client: {str(e)}'
                }
            
            try:
                print(f"DEBUG: Connecting to Telegram...")
                await client.connect()
                print(f"DEBUG: Connected successfully!")
            except Exception as e:
                print(f"ERROR: Failed to connect: {e}")
                import traceback
                traceback.print_exc()
                return {
                    'status': 'error',
                    'message': f'فشل الاتصال بـ Telegram: {str(e)}'
                }
            
            # إرسال كود التحقق
            try:
                print(f"DEBUG: Sending verification code to {phone_number}...")
                sent_code = await client.send_code(phone_number)
                print(f"DEBUG: Code sent successfully! phone_code_hash={sent_code.phone_code_hash}")
            except Exception as e:
                print(f"ERROR: Failed to send code: {e}")
                import traceback
                traceback.print_exc()
                await client.disconnect()
                return {
                    'status': 'error',
                    'message': f'فشل إرسال كود التحقق: {str(e)}'
                }
            
            # حفظ client بدون إغلاقه (Telegram يحتاجه لـ verify)
            self._active_clients[phone_number] = client
            print(f"DEBUG: Client saved in memory for phone: {phone_number}")
            print(f"DEBUG: Active clients count: {len(self._active_clients)}")
            print(f"DEBUG: IMPORTANT: Client kept alive for code verification!")
            print(f"DEBUG: Returning code_required status with phone_code_hash")
            
            return {
                'status': 'code_required',
                'phone_code_hash': sent_code.phone_code_hash,
                'message': 'أدخل كود التحقق المرسل إلى هاتفك'
            }
            
        except Exception as e:
            print(f"EXCEPTION in login_and_save_session: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'خطأ: {str(e)}'
            }
    
    async def verify_code(self, phone_number, code, phone_code_hash):
        """
        التحقق من الكود وإكمال تسجيل الدخول
        
        Args:
            phone_number: رقم الهاتف
            code: كود التحقق
            phone_code_hash: hash من المرحلة السابقة
        """
        # استيراد Pyrogram
        if not _import_pyrogram():
            return {
                'status': 'error',
                'message': 'Pyrogram غير مثبت'
            }
        
        try:
            # قراءة API credentials
            api_id = settings.TELEGRAM_API_ID
            api_hash = settings.TELEGRAM_API_HASH
            
            # التحقق والتحويل
            if not api_id or not api_hash:
                return {
                    'status': 'error',
                    'message': f'API credentials not configured'
                }
            
            try:
                api_id = int(api_id)
            except (ValueError, TypeError):
                return {
                    'status': 'error',
                    'message': f'Invalid API_ID: {api_id}'
                }
            
            print(f"DEBUG: Looking for active client for phone: {phone_number}")
            
            # الحصول على الـ client المحفوظ من login
            client = self._active_clients.get(phone_number)
            
            if not client:
                print(f"ERROR: No active client found for {phone_number}")
                print(f"ERROR: Active clients: {list(self._active_clients.keys())}")
                return {
                    'status': 'error',
                    'message': 'انتهت صلاحية الجلسة. يرجى إعادة طلب الكود.'
                }
            
            print(f"DEBUG: Found active client! Using it for verification...")
            # Client موجود بالفعل ومُتصل!
            
            should_cleanup = True  # flag لتحديد إذا نحذف client أم لا
            try:
                print(f"DEBUG: Signing in with code...")
                # تسجيل الدخول بالكود
                try:
                    await client.sign_in(phone_number, phone_code_hash, code)
                    print(f"DEBUG: Signed in successfully!")
                except Exception as e:
                    error_msg = str(e)
                    if "SESSION_PASSWORD_NEEDED" in error_msg:
                        print(f"WARNING: Two-step verification is enabled!")
                        print(f"DEBUG: Keeping client alive for password verification...")
                        should_cleanup = False  # لا نحذف client!
                        return {
                            'status': 'password_required',
                            'message': 'الحساب محمي بالتحقق بخطوتين. يرجى إدخال كلمة المرور.'
                        }
                    raise
                
                # حفظ session string المشفر
                print(f"DEBUG: Exporting session string...")
                session_string = await client.export_session_string()
                print(f"DEBUG: Session string exported!")
                
                encrypted_session = self.cipher.encrypt(session_string.encode())
                
                # حفظ في المسار الدائم
                final_session_name = self._get_session_path(phone_number)
                session_file = f"{final_session_name}_encrypted.bin"
                
                print(f"DEBUG: Saving encrypted session to {session_file}")
                with open(session_file, 'wb') as f:
                    f.write(encrypted_session)
                print(f"DEBUG: Session saved successfully!")
                
            finally:
                # فقط نُنظف إذا كان should_cleanup = True
                if should_cleanup:
                    # إغلاق الاتصال وإزالة من memory
                    try:
                        await client.disconnect()
                        print(f"DEBUG: Client disconnected successfully")
                    except Exception as e:
                        print(f"WARNING: Failed to disconnect: {e}")
                    
                    # إزالة من active clients
                    if phone_number in self._active_clients:
                        del self._active_clients[phone_number]
                        print(f"DEBUG: Active client removed from memory")
                else:
                    print(f"DEBUG: Client kept alive (password verification pending)")
            
            return {
                'status': 'success',
                'message': 'تم ربط حسابك بنجاح!',
                'session_file': session_file
            }
            
        except Exception as e:
            print(f"ERROR in verify_code: {e}")
            import traceback
            traceback.print_exc()
            
            # تنظيف في حالة الخطأ
            if phone_number in self._active_clients:
                try:
                    await self._active_clients[phone_number].disconnect()
                except:
                    pass
                del self._active_clients[phone_number]
                print(f"DEBUG: Active client cleaned up after error")
            
            return {
                'status': 'error',
                'message': f'خطأ في التحقق: {str(e)}'
            }
    
    async def verify_password(self, phone_number, password):
        """
        التحقق من كلمة المرور للحسابات المحمية بـ Two-Step Verification
        
        Args:
            phone_number: رقم الهاتف
            password: كلمة مرور Two-Step Verification
        """
        if not _import_pyrogram():
            return {
                'status': 'error',
                'message': 'Pyrogram غير مثبت'
            }
        
        try:
            # الحصول على الـ client المحفوظ
            client = self._active_clients.get(phone_number)
            
            if not client:
                return {
                    'status': 'error',
                    'message': 'انتهت صلاحية الجلسة. يرجى إعادة طلب الكود.'
                }
            
            print(f"DEBUG: Checking password for {phone_number}...")
            
            try:
                # التحقق من كلمة المرور
                await client.check_password(password)
                print(f"DEBUG: Password verified successfully!")
                
                # حفظ session
                session_string = await client.export_session_string()
                encrypted_session = self.cipher.encrypt(session_string.encode())
                
                final_session_name = self._get_session_path(phone_number)
                session_file = f"{final_session_name}_encrypted.bin"
                
                with open(session_file, 'wb') as f:
                    f.write(encrypted_session)
                
                print(f"DEBUG: Session saved successfully!")
                
                # تنظيف
                await client.disconnect()
                if phone_number in self._active_clients:
                    del self._active_clients[phone_number]
                
                return {
                    'status': 'success',
                    'message': 'تم ربط حسابك بنجاح!',
                    'session_file': session_file
                }
                
            except Exception as e:
                error_msg = str(e)
                if "PASSWORD_HASH_INVALID" in error_msg:
                    return {
                        'status': 'error',
                        'message': 'كلمة المرور غير صحيحة. حاول مرة أخرى.'
                    }
                raise
                
        except Exception as e:
            print(f"ERROR in verify_password: {e}")
            import traceback
            traceback.print_exc()
            
            # تنظيف
            if phone_number in self._active_clients:
                try:
                    await self._active_clients[phone_number].disconnect()
                except:
                    pass
                del self._active_clients[phone_number]
            
            return {
                'status': 'error',
                'message': f'خطأ في التحقق من كلمة المرور: {str(e)}'
            }
    
    def get_session_string(self, phone_number):
        """
        الحصول على session string المشفر
        
        Args:
            phone_number: رقم الهاتف
            
        Returns:
            str: session string أو None
        """
        session_name = self._get_session_path(phone_number)
        session_file = f"{session_name}_encrypted.bin"
        
        if not os.path.exists(session_file):
            return None
        
        try:
            with open(session_file, 'rb') as f:
                encrypted_session = f.read()
            
            # فك التشفير
            decrypted_session = self.cipher.decrypt(encrypted_session)
            return decrypted_session.decode()
            
        except Exception as e:
            print(f"Error decrypting session: {e}")
            return None
    
    def is_session_exists(self, phone_number):
        """التحقق من وجود session"""
        session_name = self._get_session_path(phone_number)
        session_file = f"{session_name}_encrypted.bin"
        return os.path.exists(session_file)
    
    def delete_session(self, phone_number):
        """حذف session"""
        session_name = self._get_session_path(phone_number)
        session_file = f"{session_name}_encrypted.bin"
        
        if os.path.exists(session_file):
            os.remove(session_file)
            return True
        return False
    
    async def test_session(self, phone_number):
        """اختبار session للتأكد من صلاحيتها"""
        # استيراد Pyrogram
        if not _import_pyrogram():
            return False
        
        session_string = self.get_session_string(phone_number)
        
        if not session_string:
            return False
        
        try:
            api_id = settings.TELEGRAM_API_ID
            api_hash = settings.TELEGRAM_API_HASH
            
            if not api_id or not api_hash:
                return False
            
            try:
                api_id = int(api_id)
            except (ValueError, TypeError):
                return False
            
            client = Client(
                "test_session",  # اسم الـ session
                api_id=api_id,
                api_hash=api_hash,
                session_string=session_string,
                in_memory=True
            )
            
            await client.connect()
            me = await client.get_me()
            await client.disconnect()
            
            return True if me else False
            
        except Exception as e:
            print(f"Session test failed: {e}")
            return False


# Singleton instance
session_manager = TelegramSessionManager()
