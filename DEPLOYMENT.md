# 🚀 دليل نشر SmartEdu على Render

هذا الدليل يشرح كيفية نشر المشروع على Render بأمان تام مع حماية جميع البيانات الحساسة.

---

## 📋 المتطلبات

- حساب [Render](https://render.com) (مجاني)
- حساب [Supabase](https://supabase.com) لقاعدة البيانات (مجاني)
- مفاتيح API (Telegram Bot, Gemini, إلخ)

---

## 🔐 الأمان أولاً: لا تنشر الأسرار في الكود!

### ✅ ما تم عمله لحمايتك:
- ✓ `.env` مستثنى من Git عبر `.gitignore`
- ✓ `.env.example` نموذج بدون قيم حقيقية
- ✓ جميع الأسرار ستُدار عبر Environment Variables في Render

### ⚠️ لا ترفع أبداً:
- ❌ ملف `.env` الحقيقي
- ❌ مفاتيح API في الكود
- ❌ كلمات مرور قواعد البيانات
- ❌ Tokens أو Secret Keys

---

## 📦 الخطوة 1: إعداد قاعدة البيانات (Supabase)

### 1. أنشئ مشروع جديد:
- اذهب إلى [Supabase Dashboard](https://supabase.com/dashboard)
- اضغط "New Project"
- اختر اسم، كلمة مرور قوية، ومنطقة

### 2. احصل على Database URL:
```
Settings → Database → Connection String → URI
```
سيكون بالشكل:
```
postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres
```

### 3. طبّق الـ Migrations:
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

---

## 🌐 الخطوة 2: نشر Backend على Render

### 1. أنشئ Web Service جديد:
- اذهب إلى [Render Dashboard](https://dashboard.render.com)
- اضغط "New +" → "Web Service"
- اربط GitHub Repository الخاص بك
- اختر الفرع `main`

### 2. إعدادات Build:
```
Root Directory: backend
Build Command: pip install -r requirements.txt && python manage.py collectstatic --no-input
Start Command: daphne -b 0.0.0.0 -p $PORT core.asgi:application
```

### 3. إعدادات البيئة:
اضغط "Environment" وأضف المتغيرات التالية:

#### Django Core:
```bash
PYTHON_VERSION=3.11.7
DEBUG=False
SECRET_KEY=<generate-random-50-chars>
ALLOWED_HOSTS=your-backend-name.onrender.com,localhost,127.0.0.1
```

#### Database:
```bash
DATABASE_URL=<supabase-postgres-url>
```

#### CORS & Frontend:
```bash
CORS_ALLOWED_ORIGINS=https://your-frontend-url.pages.dev
FRONTEND_URL=https://your-frontend-url.pages.dev
```

#### Email (Gmail):
```bash
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=<app-password-from-gmail>
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
```

#### JWT:
```bash
JWT_SECRET_KEY=<generate-random-32-chars>
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

#### Telegram:
```bash
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_BOT_USERNAME=<YourBotUsername>
TELEGRAM_API_ID=<your-api-id>
TELEGRAM_API_HASH=<your-api-hash>
OTP_SECRET_KEY=<generate-random-32-chars>
```

#### Gemini AI (اختياري):
```bash
GEMINI_API_KEY=<your-gemini-api-key>
```

#### File Upload:
```bash
MAX_UPLOAD_SIZE=104857600
ALLOWED_EXTENSIONS=pdf,docx,xlsx,jpg,jpeg,png,mp4,mp3,wav
```

### 4. Deploy:
- اضغط "Create Web Service"
- انتظر حتى ينتهي Build (5-10 دقائق)

---

## 🎨 الخطوة 3: نشر Frontend على Cloudflare Pages

### 1. أنشئ Pages Project:
- اذهب إلى [Cloudflare Dashboard](https://dash.cloudflare.com)
- Pages → "Create a project"
- اربط GitHub Repo
- اختر الفرع `main`

### 2. إعدادات Build:
```
Root Directory: frontend
Build Command: (leave empty)
Build Output Directory: /
```

### 3. Environment Variables:
```bash
API_BASE=https://your-backend-name.onrender.com/api
```

### 4. تحديث config.js:
في `frontend/assets/js/config.js`:
```javascript
const API_CONFIG = {
  BASE_URL: 'https://your-backend-name.onrender.com/api'
};
```

---

## 🔄 الخطوة 4: تحديث Backend CORS

عُد إلى Render Backend → Environment وحدّث:
```bash
CORS_ALLOWED_ORIGINS=https://your-frontend-url.pages.dev
FRONTEND_URL=https://your-frontend-url.pages.dev
ALLOWED_HOSTS=your-backend-name.onrender.com
```

---

## 🤖 الخطوة 5: تشغيل Telegram Bot

### خيار 1: استضافة منفصلة (موصى به):
- أنشئ Background Worker في Render:
  ```
  Root Directory: telegram_bot
  Start Command: python bot.py
  ```
- أضف نفس Environment Variables (خاصة TELEGRAM_BOT_TOKEN)

### خيار 2: تشغيل محلي:
```bash
cd telegram_bot
python bot.py
```

---

## ✅ الخطوة 6: اختبار النشر

### 1. تحقق من Backend:
```bash
curl https://your-backend-name.onrender.com/api/
```

### 2. تحقق من Frontend:
افتح: `https://your-frontend-url.pages.dev`

### 3. اختبر تسجيل الدخول:
- سجّل حساب جديد
- تحقق من وصول Email التفعيل
- سجّل دخول

### 4. اختبر Telegram:
- أرسل `/start` للبوت
- اختبر إرسال OTP

---

## 🔧 استكشاف الأخطاء

### خطأ: `CORS Error`
**الحل**: تأكد من `CORS_ALLOWED_ORIGINS` في Backend يطابق عنوان Frontend بالضبط

### خطأ: `Database Connection Error`
**الحل**: تحقق من صحة `DATABASE_URL` في Environment Variables

### خطأ: `Telegram Bot Not Responding`
**الحل**: 
1. تحقق من `TELEGRAM_BOT_TOKEN`
2. تأكد أن Bot Worker يعمل
3. راجع Logs في Render

### خطأ: `Static Files 404`
**الحل**: تأكد من تشغيل `collectstatic` في Build Command

---

## 📊 مراقبة الأداء

### Render Logs:
```
Dashboard → Your Service → Logs
```

### Supabase Logs:
```
Dashboard → Logs → API Logs
```

---

## 🔐 توليد Secrets عشوائية

### في Python:
```python
import secrets
print(secrets.token_urlsafe(32))  # للـ SECRET_KEY
print(secrets.token_urlsafe(24))  # للـ JWT_SECRET_KEY
```

### في PowerShell:
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

---

## 📚 موارد إضافية

- [Render Docs](https://render.com/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

## ⚠️ ملاحظات أمان مهمة

1. **لا تشارك ملف `.env` أبداً**
2. **دوّر (غيّر) جميع Secrets بعد النشر**
3. **فعّل 2FA على جميع الحسابات**
4. **راقب Logs بانتظام للكشف عن أي نشاط مشبوه**
5. **استخدم HTTPS فقط في الإنتاج**
6. **قيّد CORS على نطاقك فقط**

---

## 📞 الدعم

للمساعدة أو الإبلاغ عن مشاكل، افتح Issue في GitHub Repository.

---

**تم التحديث**: أكتوبر 2025
