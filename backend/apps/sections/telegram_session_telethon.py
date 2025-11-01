"""
Telegram Session Manager - Telethon Version
إدارة sessions باستخدام Telethon
"""
import os
from django.conf import settings

try:
    from telethon import TelegramClient, errors
    from telethon.tl import functions as tl_functions, types as tl_types
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    TelegramClient = None
    errors = None
    tl_types = None
    tl_functions = None


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
    
    async def login_and_save_session(self, phone_number, force_sms=True):
        """
        إرسال كود التحقق وحفظ client مؤقتاً
        """
        print(f"\n{'='*60}")
        print(f"📱 login_and_save_session called for: {phone_number}")
        print(f"{'='*60}")
        
        if not TELETHON_AVAILABLE:
            print("❌ Telethon not available!")
            return {
                'status': 'error',
                'message': 'Telethon غير مثبت. يرجى تثبيته على السيرفر.'
            }
        
        try:
            api_id = settings.TELEGRAM_API_ID
            api_hash = settings.TELEGRAM_API_HASH
            
            print(f"🔑 API Credentials: api_id={api_id}, api_hash={'*' * 10 if api_hash else 'None'}")
            
            if not api_id or not api_hash:
                print("❌ Missing API credentials!")
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
            
            # التحقق من وجود جلسة صالحة (بفحص حقيقي!)
            is_valid_session = False
            try:
                if await client.is_user_authorized():
                    # تحقق إضافي: جرب الحصول على معلومات المستخدم
                    try:
                        me = await client.get_me()
                        if me and me.phone:
                            print(f"✅ Valid session found for: {me.phone}")
                            is_valid_session = True
                    except Exception as get_me_error:
                        print(f"⚠️ Session claims authorized but get_me() failed: {get_me_error}")
                        is_valid_session = False
            except Exception as auth_error:
                print(f"⚠️ is_user_authorized() failed: {auth_error}")
                is_valid_session = False
            
            if is_valid_session:
                await client.disconnect()
                return {
                    'status': 'already_connected',
                    'message': 'حسابك مربوط مسبقاً!'
                }
            
            # Session غير صالح أو غير موجود، احذفه
            if not is_valid_session:
                print(f"🗑️ Removing invalid session for: {phone_number}")
                try:
                    await client.disconnect()
                    if os.path.exists(session_path + '.session'):
                        os.remove(session_path + '.session')
                        print(f"✅ Session file deleted")
                except Exception as del_error:
                    print(f"⚠️ Error deleting session: {del_error}")
                
                # أعد الاتصال بـ session نظيف
                client = TelegramClient(session_path, int(api_id), api_hash)
                await client.connect()
                print(f"🔄 Fresh client connected")
            
            # إرسال كود التحقق
            print(f"📤 Sending code request to: {phone_number} | force_sms={force_sms}")
            try:
                if force_sms:
                    sent = await client.send_code_request(phone_number, force_sms=True)
                else:
                    sent = await client.send_code_request(phone_number)
                # Determine delivery type
                delivery = 'unknown'
                try:
                    if tl_types is not None:
                        if isinstance(sent.type, tl_types.auth.SentCodeTypeSms):
                            delivery = 'sms'
                        elif isinstance(sent.type, tl_types.auth.SentCodeTypeApp):
                            delivery = 'app'
                        elif isinstance(sent.type, tl_types.auth.SentCodeTypeCall):
                            delivery = 'call'
                        elif isinstance(sent.type, tl_types.auth.SentCodeTypeFlashCall):
                            delivery = 'flash_call'
                except Exception as _:
                    pass
                print(f"✅ Code sent! phone_code_hash: {str(sent.phone_code_hash)[:10]}... | delivery={delivery}")
            except errors.FloodWaitError as e:
                print(f"❌ FloodWaitError: {e.seconds} seconds")
                await client.disconnect()
                return {
                    'status': 'error',
                    'message': f'يرجى الانتظار {e.seconds} ثانية قبل المحاولة مرة أخرى (Telegram Flood Control)'
                }
            except errors.PhoneNumberInvalidError:
                print(f"❌ Invalid phone number: {phone_number}")
                await client.disconnect()
                return {
                    'status': 'error',
                    'message': f'رقم الهاتف غير صحيح: {phone_number}'
                }
            except Exception as send_error:
                print(f"❌ Send code error: {send_error}")
                import traceback
                traceback.print_exc()
                await client.disconnect()
                return {
                    'status': 'error',
                    'message': f'فشل إرسال الكود: {str(send_error)}'
                }
            
            # حفظ client مؤقتاً
            self._active_clients[phone_number] = (client, sent.phone_code_hash)
            
            return {
                'status': 'code_required',
                'phone_code_hash': sent.phone_code_hash,
                'message': 'تم إرسال كود التحقق',
                'delivery': delivery if 'delivery' in locals() else 'unknown',
                'force_sms': force_sms
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
        """التحقق من كلمة مرور 2FA"""
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
    
    async def resend_code(self, phone_number):
        """إعادة إرسال كود التحقق"""
        try:
            if not TELETHON_AVAILABLE or tl_functions is None:
                return {
                    'status': 'error',
                    'message': 'Telethon غير متاح'
                }
            
            if phone_number not in self._active_clients:
                return {
                    'status': 'error',
                    'message': 'لا توجد جلسة نشطة. اطلب الكود أولاً.'
                }
            
            client, saved_hash = self._active_clients[phone_number]
            print(f"🔁 Resending code for: {phone_number}")
            
            try:
                sent = await client(tl_functions.auth.ResendCode(
                    phone_number=phone_number,
                    phone_code_hash=saved_hash
                ))
            except errors.FloodWaitError as e:
                return {
                    'status': 'error',
                    'message': f'يرجى الانتظار {e.seconds} ثانية'
                }
            except Exception as e:
                print(f"❌ Resend error: {e}")
                return {
                    'status': 'error',
                    'message': f'فشل إعادة الإرسال: {str(e)}'
                }
            
            # تحديد نوع التوصيل
            def _type_name(t):
                try:
                    return type(t).__name__.replace('SentCodeType', '').lower()
                except:
                    return 'unknown'
            
            delivery = _type_name(getattr(sent, 'type', None))
            next_delivery = _type_name(getattr(sent, 'next_type', None))
            
            # تحديث hash
            self._active_clients[phone_number] = (client, sent.phone_code_hash)
            
            print(f"✅ Code resent! delivery: {delivery}, next: {next_delivery}")
            
            return {
                'status': 'code_resent',
                'phone_code_hash': sent.phone_code_hash,
                'delivery': delivery,
                'next_delivery': next_delivery,
                'message': 'تمت إعادة إرسال الكود'
            }
        except Exception as e:
            print(f"❌ Resend fatal error: {e}")
            return {
                'status': 'error',
                'message': f'خطأ: {str(e)}'
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
