"""
Telegram Bot Utilities
"""
import re
import hmac
import hashlib
import requests
from config import BotConfig


class TelegramHelper:
    """مساعد تيليجرام"""
    
    @staticmethod
    def extract_group_id(telegram_link):
        """
        استخراج معرّف القروب من رابط تيليجرام
        
        Args:
            telegram_link (str): رابط القروب
            
        Returns:
            str: معرّف القروب أو None
        """
        if not telegram_link:
            return None
        
        # أنماط الروابط المختلفة
        patterns = [
            r't\.me/joinchat/([A-Za-z0-9_-]+)',      # https://t.me/joinchat/xxxxx
            r't\.me/\+([A-Za-z0-9_-]+)',              # https://t.me/+xxxxx
            r'@(\w+)',                                 # @username
        ]
        
        for pattern in patterns:
            match = re.search(pattern, telegram_link)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def verify_signature(signed_data, secret_key):
        """
        التحقق من توقيع البيانات
        
        Args:
            signed_data (str): البيانات الموقعة (data|signature)
            secret_key (str): المفتاح السري
            
        Returns:
            str or None: البيانات إذا كان التوقيع صحيح
        """
        try:
            data, signature = signed_data.rsplit('|', 1)
            
            expected_sig = hmac.new(
                secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_sig):
                return data
            
            return None
        except:
            return None


class APIClient:
    """عميل للتواصل مع Backend API"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url or BotConfig.API_BASE_URL
        self.session = requests.Session()
    
    def get_otp_record(self, otp_id):
        """
        جلب سجل OTP من API
        
        Args:
            otp_id (str): معرّف OTP
            
        Returns:
            dict: بيانات OTP
        """
        try:
            # في النظام الحقيقي، يجب استخدام API endpoint
            # لكن هنا سنستخدم الاتصال المباشر بقاعدة البيانات
            return self._get_otp_from_db(otp_id)
        except Exception as e:
            print(f"Error fetching OTP: {e}")
            return None
    
    def _get_otp_from_db(self, otp_id):
        """جلب OTP من قاعدة البيانات مباشرة"""
        # سيتم تنفيذه في الكود الفعلي
        pass
    
    def update_otp_telegram_info(self, otp_id, user_id, chat_id, username=None):
        """
        تحديث معلومات تيليجرام في سجل OTP
        
        Args:
            otp_id (str): معرّف OTP
            user_id (int): معرّف المستخدم
            chat_id (int): معرّف المحادثة
            username (str): اسم المستخدم
        """
        # سيتم تنفيذه في الكود الفعلي
        pass
    
    def log_bot_action(self, otp_id, action, details=None):
        """
        تسجيل حدث في OTPLog
        
        Args:
            otp_id (str): معرّف OTP
            action (str): الإجراء
            details (str): التفاصيل
        """
        # سيتم تنفيذه في الكود الفعلي
        pass


class MessageFormatter:
    """منسّق الرسائل"""
    
    @staticmethod
    def welcome_message(student_name):
        """رسالة الترحيب"""
        return f"""
👋 أهلاً {student_name}!

مرحباً بك في بوت التحقق من تسليم المشاريع.

للحصول على رمز التسليم:
1️⃣ انقر على الرابط من صفحة المشروع
2️⃣ تأكد من انضمامك لقروب الشعبة
3️⃣ استلم الرمز هنا

دعنا نبدأ! 🚀
"""
    
    @staticmethod
    def send_otp_code(student_name, code, expires_minutes=10):
        """رسالة إرسال الكود"""
        return f"""
🎉 تم التحقق بنجاح!

👤 الطالب: {student_name}
🔐 رمز التسليم: *{code}*

⏳ صالح لمدة {expires_minutes} دقائق فقط

📌 الخطوات التالية:
1️⃣ انسخ الرمز أعلاه
2️⃣ ارجع لصفحة المشروع
3️⃣ أدخل الرمز في الحقل المخصص
4️⃣ ارفع مشروعك

⚠️ لا تشارك هذا الرمز مع أحد!
"""
    
    @staticmethod
    def not_member_message(group_link):
        """رسالة عدم العضوية"""
        return f"""
⚠️ غير مسموح!

يجب أن تكون عضواً في قروب الشعبة أولاً للحصول على رمز التسليم.

🔗 انضم للقروب من هنا:
{group_link}

بعد الانضمام، أعد فتح الرابط من صفحة المشروع.
"""
    
    @staticmethod
    def error_message(error_type='general'):
        """رسائل الأخطاء"""
        messages = {
            'general': """
❌ حدث خطأ!

عذراً، حدث خطأ أثناء معالجة طلبك.
الرجاء المحاولة مرة أخرى أو التواصل مع المعلم.
""",
            'expired': """
⏰ انتهت الصلاحية!

الرابط الذي استخدمته منتهي الصلاحية.
الرجاء طلب رمز جديد من صفحة المشروع.
""",
            'invalid_link': """
🔗 رابط غير صحيح!

الرابط الذي استخدمته غير صالح.
تأكد من فتح الرابط من صفحة المشروع مباشرة.
""",
            'already_used': """
✅ مستخدم بالفعل!

هذا الرمز تم استخدامه من قبل.
إذا كنت بحاجة لرمز جديد، اطلبه من صفحة المشروع.
"""
        }
        
        return messages.get(error_type, messages['general'])
    
    @staticmethod
    def help_message():
        """رسالة المساعدة"""
        return """
📚 كيفية الاستخدام:

1️⃣ افتح رابط المشروع من موقع المعلم
2️⃣ أدخل اسمك واضغط "الحصول على رمز"
3️⃣ ستُفتح صفحة البوت تلقائياً
4️⃣ سيتحقق البوت من عضويتك في القروب
5️⃣ إذا كنت عضواً، ستستلم الرمز هنا
6️⃣ انسخ الرمز وأدخله في صفحة المشروع
7️⃣ ارفع ملف مشروعك

⚠️ ملاحظات مهمة:
• يجب أن تكون عضواً في قروب الشعبة
• الرمز صالح لمدة 10 دقائق فقط
• لا تشارك الرمز مع أحد
• يمكنك المحاولة 5 مرات فقط

💡 إذا واجهت مشكلة، تواصل مع معلمك.
"""


class DatabaseHelper:
    """مساعد قاعدة البيانات"""
    
    def __init__(self, db_url=None):
        self.db_url = db_url or BotConfig.DATABASE_URL
        self.connection = None
    
    def connect(self):
        """الاتصال بقاعدة البيانات"""
        import psycopg2
        try:
            self.connection = psycopg2.connect(self.db_url)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def get_otp_record(self, otp_id):
        """جلب سجل OTP"""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT 
                    po.id, po.code, po.student_name, po.status,
                    p.id as project_id, p.title as project_title,
                    s.id as section_id, s.section_name,
                    sl.telegram_link
                FROM project_otp po
                JOIN projects p ON po.project_id = p.id
                LEFT JOIN sections s ON p.section_id = s.id
                LEFT JOIN section_links sl ON s.id = sl.section_id
                WHERE po.id = %s
            """
            
            cursor.execute(query, (otp_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'code': row[1],
                    'student_name': row[2],
                    'status': row[3],
                    'project_id': row[4],
                    'project_title': row[5],
                    'section_id': row[6],
                    'section_name': row[7],
                    'telegram_link': row[8]
                }
            
            return None
            
        except Exception as e:
            print(f"Database query error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def update_otp_telegram_info(self, otp_id, user_id, chat_id, username=None):
        """تحديث معلومات تيليجرام"""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE project_otp
                SET telegram_user_id = %s,
                    telegram_chat_id = %s,
                    telegram_username = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            
            cursor.execute(query, (user_id, chat_id, username, otp_id))
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Database update error: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def create_log(self, otp_id, action, details=None):
        """إنشاء سجل في otp_logs"""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO otp_logs (otp_id, action, details, created_at)
                VALUES (%s, %s, %s, NOW())
            """
            
            cursor.execute(query, (otp_id, action, details))
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Database insert error: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """إغلاق الاتصال"""
        if self.connection:
            self.connection.close()
