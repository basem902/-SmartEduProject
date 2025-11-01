# Telegram Service - FastAPI

خدمة منفصلة لإدارة جلسات Telegram باستخدام FastAPI و Telethon.

## 📦 التثبيت

### 1. إنشاء بيئة افتراضية

```bash
cd telegram_service
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### 3. إعداد المتغيرات

```bash
# انسخ .env.example إلى .env
copy .env.example .env

# ثم عدّل القيم في .env
```

## 🚀 التشغيل

### محلياً (Development)

```bash
# من داخل telegram_service/
python main.py
```

أو:

```bash
uvicorn main:app --reload --port 8001
```

### على Render

1. **إنشاء Web Service جديد**
2. **الإعدادات:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables:**
   ```
   TELEGRAM_API_ID=26671326
   TELEGRAM_API_HASH=996fd0da7abec92881f41addceca3677
   TELEGRAM_BOT_TOKEN=7431625101:AAGR-rk1GbpdawfVCwBpTnnYGWu-aYVXTV4
   TELEGRAM_BOT_USERNAME=SmartEduProjectBot
   OTP_SECRET_KEY=sEcReT_2025_SmArTeDu_OtP_kEy_987654321
   ```

## 📡 API Endpoints

### Base URL
```
http://localhost:8001
```

### 1. إرسال كود التحقق

```http
POST /telegram/send-code
Content-Type: application/json

{
  "phone_number": "+966558048004"
}
```

**Response:**
```json
{
  "status": "code_sent",
  "phone_code_hash": "abc123...",
  "delivery": "app",
  "message": "تم إرسال الكود بنجاح"
}
```

### 2. إعادة إرسال الكود

```http
POST /telegram/resend-code
Content-Type: application/json

{
  "phone_number": "+966558048004"
}
```

**Response:**
```json
{
  "status": "code_resent",
  "phone_code_hash": "xyz789...",
  "delivery": "call",
  "next_delivery": "sms",
  "message": "تمت إعادة إرسال الكود"
}
```

### 3. التحقق من الكود

```http
POST /telegram/verify-code
Content-Type: application/json

{
  "phone_number": "+966558048004",
  "code": "12345",
  "phone_code_hash": "abc123..."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "تم ربط الحساب بنجاح!"
}
```

أو إذا كان 2FA مفعّل:
```json
{
  "status": "password_required",
  "message": "يرجى إدخال كلمة مرور التحقق بخطوتين"
}
```

### 4. التحقق من كلمة المرور (2FA)

```http
POST /telegram/verify-password
Content-Type: application/json

{
  "phone_number": "+966558048004",
  "password": "my_password"
}
```

### 5. حالة الجلسة

```http
GET /telegram/session-status?phone_number=%2B966558048004
```

**Response:**
```json
{
  "phone_number": "+966558048004",
  "session_exists": true,
  "status": "connected"
}
```

### 6. حذف الجلسة

```http
DELETE /telegram/delete-session
Content-Type: application/json

{
  "phone_number": "+966558048004"
}
```

## 🔗 التكامل مع Django

في Django backend، استخدم `requests` للاتصال بـ FastAPI:

```python
import requests

FASTAPI_URL = "http://localhost:8001"  # أو URL على Render

# إرسال كود
response = requests.post(
    f"{FASTAPI_URL}/telegram/send-code",
    json={"phone_number": "+966558048004"}
)
data = response.json()
```

## 📝 ملاحظات

- **Sessions:** تُحفظ في مجلد `sessions/` داخل `telegram_service/`
- **Port:** الافتراضي 8001 (يمكن تغييره في `.env`)
- **CORS:** مفتوح للجميع في Development (عدّله للإنتاج)

## 🐛 استكشاف الأخطاء

### الكود لا يصل؟

1. تحقق من Telegram App (ليس SMS دائماً)
2. ابحث عن محادثة "Telegram" الرسمية
3. افحص Saved Messages
4. جرب "إعادة إرسال" للحصول على مكالمة

### FloodWaitError؟

انتظر المدة المحددة قبل إعادة المحاولة.

### API_ID/HASH خاطئ؟

تأكد من القيم في `.env` من https://my.telegram.org/apps
