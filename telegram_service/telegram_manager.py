"""
Telegram Manager - FastAPI Service
إدارة Telegram Sessions باستخدام Telethon
"""
import os
import asyncio
from pathlib import Path
from typing import Dict, Optional, Tuple
from telethon import TelegramClient, errors
from telethon.tl import functions as tl_functions, types as tl_types


class TelegramSessionManager:
    """إدارة جلسات Telegram"""
    
    def __init__(self, api_id: int, api_hash: str, sessions_dir: str = "sessions"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        self._active_clients: Dict[str, Tuple[TelegramClient, str]] = {}
    
    def _get_session_path(self, phone_number: str) -> Path:
        """الحصول على مسار session"""
        clean_phone = phone_number.replace('+', '').replace(' ', '')
        return self.sessions_dir / f"session_{clean_phone}"
    
    async def send_code(self, phone_number: str) -> dict:
        """إرسال كود التحقق"""
        print(f"\n{'='*60}")
        print(f"📱 Sending code to: {phone_number}")
        print(f"{'='*60}")
        
        try:
            session_path = self._get_session_path(phone_number)
            client = TelegramClient(str(session_path), self.api_id, self.api_hash)
            
            await client.connect()
            
            # فحص الجلسة الحالية
            is_valid = False
            try:
                if await client.is_user_authorized():
                    me = await client.get_me()
                    if me and me.phone:
                        print(f"✅ Valid session found for: {me.phone}")
                        is_valid = True
            except Exception as e:
                print(f"⚠️ Session check failed: {e}")
            
            if is_valid:
                await client.disconnect()
                return {
                    'status': 'already_connected',
                    'message': 'حسابك مربوط مسبقاً!'
                }
            
            # حذف session غير صالح
            if not is_valid:
                print(f"🗑️ Removing invalid session")
                try:
                    await client.disconnect()
                    if session_path.with_suffix('.session').exists():
                        session_path.with_suffix('.session').unlink()
                        print(f"✅ Session deleted")
                except Exception as e:
                    print(f"⚠️ Delete error: {e}")
                
                client = TelegramClient(str(session_path), self.api_id, self.api_hash)
                await client.connect()
                print(f"🔄 Fresh client connected")
            
            # إرسال الكود
            print(f"📤 Sending code request...")
            try:
                sent = await client.send_code_request(phone_number)
                
                # تحديد نوع التوصيل
                delivery = 'unknown'
                try:
                    if isinstance(sent.type, tl_types.auth.SentCodeTypeSms):
                        delivery = 'sms'
                    elif isinstance(sent.type, tl_types.auth.SentCodeTypeApp):
                        delivery = 'app'
                    elif isinstance(sent.type, tl_types.auth.SentCodeTypeCall):
                        delivery = 'call'
                    elif isinstance(sent.type, tl_types.auth.SentCodeTypeFlashCall):
                        delivery = 'flash_call'
                except:
                    pass
                
                print(f"✅ Code sent! hash: {sent.phone_code_hash[:10]}... | delivery: {delivery}")
                
                # حفظ client
                self._active_clients[phone_number] = (client, sent.phone_code_hash)
                
                return {
                    'status': 'code_sent',
                    'phone_code_hash': sent.phone_code_hash,
                    'delivery': delivery,
                    'message': 'تم إرسال الكود بنجاح'
                }
                
            except errors.FloodWaitError as e:
                print(f"❌ FloodWaitError: {e.seconds}s")
                await client.disconnect()
                return {
                    'status': 'error',
                    'message': f'يرجى الانتظار {e.seconds} ثانية'
                }
            except errors.PhoneNumberInvalidError:
                print(f"❌ Invalid phone number")
                await client.disconnect()
                return {
                    'status': 'error',
                    'message': 'رقم الهاتف غير صحيح'
                }
            except Exception as e:
                print(f"❌ Send error: {e}")
                await client.disconnect()
                return {
                    'status': 'error',
                    'message': f'فشل إرسال الكود: {str(e)}'
                }
        
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'خطأ: {str(e)}'
            }
    
    async def resend_code(self, phone_number: str) -> dict:
        """إعادة إرسال الكود"""
        print(f"🔁 Resending code for: {phone_number}")
        
        if phone_number not in self._active_clients:
            return {
                'status': 'error',
                'message': 'لا توجد جلسة نشطة. اطلب الكود أولاً.'
            }
        
        try:
            client, saved_hash = self._active_clients[phone_number]
            
            sent = await client(tl_functions.auth.ResendCode(
                phone_number=phone_number,
                phone_code_hash=saved_hash
            ))
            
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
    
    async def verify_code(self, phone_number: str, code: str, phone_code_hash: str) -> dict:
        """التحقق من الكود"""
        print(f"🔐 Verifying code for: {phone_number}")
        
        if phone_number not in self._active_clients:
            return {
                'status': 'error',
                'message': 'انتهت صلاحية الجلسة'
            }
        
        try:
            client, saved_hash = self._active_clients[phone_number]
            
            await client.sign_in(
                phone=phone_number,
                code=code,
                phone_code_hash=saved_hash
            )
            
            print(f"✅ Code verified successfully!")
            
            await client.disconnect()
            del self._active_clients[phone_number]
            
            return {
                'status': 'success',
                'message': 'تم ربط الحساب بنجاح!'
            }
            
        except errors.SessionPasswordNeededError:
            print(f"🔒 2FA required")
            return {
                'status': 'password_required',
                'message': 'يرجى إدخال كلمة مرور التحقق بخطوتين'
            }
        except errors.PhoneCodeInvalidError:
            print(f"❌ Invalid code")
            return {
                'status': 'error',
                'message': 'الكود غير صحيح'
            }
        except errors.PhoneCodeExpiredError:
            print(f"❌ Code expired")
            # تنظيف
            if phone_number in self._active_clients:
                try:
                    await self._active_clients[phone_number][0].disconnect()
                except:
                    pass
                del self._active_clients[phone_number]
            return {
                'status': 'error',
                'message': 'انتهت صلاحية الكود. اطلب كوداً جديداً.'
            }
        except Exception as e:
            print(f"❌ Verify error: {e}")
            # تنظيف
            if phone_number in self._active_clients:
                try:
                    await self._active_clients[phone_number][0].disconnect()
                except:
                    pass
                del self._active_clients[phone_number]
            return {
                'status': 'error',
                'message': f'فشل التحقق: {str(e)}'
            }
    
    async def verify_password(self, phone_number: str, password: str) -> dict:
        """التحقق من كلمة مرور 2FA"""
        print(f"🔐 Verifying 2FA password for: {phone_number}")
        
        if phone_number not in self._active_clients:
            return {
                'status': 'error',
                'message': 'انتهت صلاحية الجلسة'
            }
        
        try:
            client, _ = self._active_clients[phone_number]
            
            await client.sign_in(password=password)
            
            print(f"✅ 2FA verified successfully!")
            
            await client.disconnect()
            del self._active_clients[phone_number]
            
            return {
                'status': 'success',
                'message': 'تم ربط الحساب بنجاح!'
            }
            
        except errors.PasswordHashInvalidError:
            print(f"❌ Invalid password")
            return {
                'status': 'error',
                'message': 'كلمة المرور غير صحيحة'
            }
        except Exception as e:
            print(f"❌ Password verify error: {e}")
            # تنظيف
            if phone_number in self._active_clients:
                try:
                    await self._active_clients[phone_number][0].disconnect()
                except:
                    pass
                del self._active_clients[phone_number]
            return {
                'status': 'error',
                'message': f'فشل التحقق: {str(e)}'
            }
    
    def is_session_exists(self, phone_number: str) -> bool:
        """التحقق من وجود session"""
        session_path = self._get_session_path(phone_number)
        return session_path.with_suffix('.session').exists()
    
    def delete_session(self, phone_number: str) -> bool:
        """حذف session"""
        session_path = self._get_session_path(phone_number)
        session_file = session_path.with_suffix('.session')
        
        try:
            if session_file.exists():
                session_file.unlink()
                # حذف journal
                journal = session_path.with_suffix('.session-journal')
                if journal.exists():
                    journal.unlink()
                print(f"✅ Session deleted: {phone_number}")
                return True
        except Exception as e:
            print(f"❌ Delete error: {e}")
        
        return False
