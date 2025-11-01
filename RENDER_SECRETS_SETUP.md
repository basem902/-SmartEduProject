# 🚀 دليل سريع: إعداد Secrets في Render

## 📋 قائمة Environment Variables المطلوبة

### Backend Service

```env
# Django Core
SECRET_KEY=<generate-random-50-chars>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com

# Database (يتم ملؤها تلقائياً من Render Database)
DATABASE_URL=<auto-filled-by-render>

# Email
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=<your-gmail-app-password>
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465

# Telegram
TELEGRAM_API_ID=26671326
TELEGRAM_API_HASH=996fd0da7abec92881f41addceca3677
TELEGRAM_BOT_TOKEN=7431625101:AAHinybqVQmZRSHN23VylqZZm_lJoi67_Wk
TELEGRAM_BOT_USERNAME=SmartEduProjectBot

# Security
OTP_SECRET_KEY=<generate-random-string>
JWT_SECRET_KEY=<generate-random-string>
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS
CORS_ALLOWED_ORIGINS=https://smartedu-basem.netlify.app,https://yourdomain.com

# Frontend
FRONTEND_URL=https://smartedu-basem.netlify.app

# File Upload
MAX_UPLOAD_SIZE=104857600
ALLOWED_EXTENSIONS=pdf,docx,xlsx,jpg,jpeg,png,mp4,mp3,wav
```

---

## 🔧 الخطوات التفصيلية

### 1️⃣ افتح Render Dashboard
👉 https://dashboard.render.com

### 2️⃣ اختر Backend Service
- من القائمة، اختر service الخاص بالـ Backend
- (مثلاً: `smartedu-backend`)

### 3️⃣ اذهب إلى Environment
- من القائمة اليسرى: **Environment**
- ستظهر قائمة بالمتغيرات الحالية

### 4️⃣ أضف/حدّث المتغيرات

#### الطريقة 1: إضافة واحدة واحدة

```
1. اضغط "Add Environment Variable"
2. Key: SECRET_KEY
3. Value: <paste-your-secret-key>
4. اضغط "Add"
5. كرر للباقي
```

#### الطريقة 2: رفع دفعة واحدة (الأسرع)

```
1. اضغط "Add from .env"
2. الصق محتوى .env (أو انسخ من القائمة أعلاه)
3. اضغط "Add variables"
```

### 5️⃣ احفظ التغييرات
- بعد إضافة كل المتغيرات
- اضغط **"Save Changes"** في الأسفل

### 6️⃣ أعد Deploy
- في أعلى الصفحة
- اضغط **"Manual Deploy"**
- اختر **"Deploy latest commit"**
- انتظر 2-3 دقائق

### 7️⃣ تحقق من Logs
- اضغط على تبويب **"Logs"**
- ابحث عن:
  - ✅ `Starting server...`
  - ✅ `Connected to database`
  - ❌ أي أخطاء

---

## 🔑 توليد القيم العشوائية

### SECRET_KEY (Django)

**في Terminal:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**أو عبر الإنترنت:**
- https://djecrety.ir/

### JWT_SECRET_KEY & OTP_SECRET_KEY

**في Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**أو:**
```bash
openssl rand -base64 32
```

---

## 📝 نصائح مهمة

### ✅ افعل:

1. **استخدم قيم مختلفة لكل بيئة**
   - Production ≠ Development
   - كل service له secrets خاصة

2. **اختبر بعد Deploy**
   - افتح الموقع
   - جرّب كل feature
   - تحقق من Logs

3. **احفظ نسخة احتياطية**
   - في password manager (1Password/Bitwarden)
   - أو ملف محلي مشفر
   - **لا ترفعها على Git!**

### ❌ لا تفعل:

1. **لا تستخدم قيم .env.example**
   - هي للمثال فقط!
   - استبدلها بقيم حقيقية

2. **لا تشارك Secrets**
   - في Slack/Discord
   - في Screenshots
   - في Git

3. **لا تترك DEBUG=True**
   - في Production
   - خطر أمني كبير!

---

## 🌐 Telegram Service (إذا كان منفصلاً)

إذا كان لديك service منفصل لـ telegram_service:

### المتغيرات المطلوبة:

```env
TELEGRAM_API_ID=26671326
TELEGRAM_API_HASH=996fd0da7abec92881f41addceca3677
TELEGRAM_BOT_TOKEN=7431625101:AAHinybqVQmZRSHN23VylqZZm_lJoi67_Wk
TELEGRAM_BOT_USERNAME=SmartEduProjectBot
OTP_SECRET_KEY=<same-as-backend>
```

### الخطوات:
1. افتح Telegram Service في Render
2. Environment
3. أضف المتغيرات أعلاه
4. Save Changes
5. Manual Deploy

---

## 🎯 Netlify (Frontend)

### 1️⃣ افتح Netlify Dashboard
👉 https://app.netlify.com

### 2️⃣ اختر موقعك
- من القائمة، اختر `smartedu-basem`

### 3️⃣ اذهب إلى Environment Variables
```
Site settings → Environment variables
```

### 4️⃣ أضف المتغيرات

```
Key: VITE_API_URL
Value: https://your-backend.onrender.com/api

Key: VITE_TELEGRAM_SERVICE_URL
Value: https://your-telegram-service.onrender.com

Key: VITE_ENABLE_TELEGRAM
Value: true
```

### 5️⃣ أعد Deploy
```
Deploys → Trigger deploy → Clear cache and deploy
```

---

## ✅ Checklist النهائي

### Backend (Render):
- [ ] SECRET_KEY - تم توليده عشوائياً
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS - يحتوي على domain Render
- [ ] DATABASE_URL - تم ملؤه تلقائياً
- [ ] SMTP_EMAIL - بريدك الإلكتروني
- [ ] SMTP_PASSWORD - App Password من Gmail
- [ ] TELEGRAM_BOT_TOKEN - **التوكن الجديد** ✅
- [ ] TELEGRAM_API_ID & HASH - من my.telegram.org
- [ ] OTP_SECRET_KEY - تم توليده عشوائياً
- [ ] JWT_SECRET_KEY - تم توليده عشوائياً
- [ ] CORS_ALLOWED_ORIGINS - يحتوي على Netlify URL
- [ ] FRONTEND_URL - Netlify URL
- [ ] Manual Deploy - تم بنجاح
- [ ] Logs - لا أخطاء

### Telegram Service (إذا كان منفصلاً):
- [ ] TELEGRAM_BOT_TOKEN - نفس القيمة من Backend
- [ ] TELEGRAM_API_ID & HASH
- [ ] Manual Deploy - تم بنجاح

### Frontend (Netlify):
- [ ] VITE_API_URL - Backend URL
- [ ] VITE_TELEGRAM_SERVICE_URL - Service URL
- [ ] Clear cache and deploy - تم بنجاح

### اختبار:
- [ ] الموقع يفتح ✅
- [ ] تسجيل الدخول يعمل ✅
- [ ] إرسال كود Telegram يعمل ✅
- [ ] لا أخطاء في Console ✅

---

## 🆘 حل المشاكل

### المشكلة: "Internal Server Error 500"

**الأسباب المحتملة:**
1. SECRET_KEY غير موجود أو فارغ
2. DATABASE_URL غير صحيح
3. متغير مطلوب ناقص

**الحل:**
- افحص Logs في Render
- تأكد من جميع المتغيرات المطلوبة
- أعد Deploy

### المشكلة: "CORS Error"

**السبب:**
- CORS_ALLOWED_ORIGINS لا يحتوي على Netlify URL

**الحل:**
```env
CORS_ALLOWED_ORIGINS=https://smartedu-basem.netlify.app,https://yourdomain.com
```

### المشكلة: "Telegram code not sent"

**السبب:**
- TELEGRAM_BOT_TOKEN خاطئ أو قديم

**الحل:**
- تأكد من التوكن الجديد: `7431625101:AAHinybqVQmZRSHN23VylqZZm_lJoi67_Wk`
- أعد Deploy بعد التحديث

---

## 🔄 بعد الانتهاء

### احذف ملفات مؤقتة:

```bash
del UPDATE_TOKEN_INSTRUCTIONS.txt
del TELEGRAM_CODE_SEARCH_GUIDE.md
```

(احتفظ بـ SECRETS_MANAGEMENT_GUIDE.md للمرجع)

### راقب الأداء:

- افحص Logs بانتظام
- راقب استخدام Database
- راقب استخدام API (إذا كان محدوداً)

### دوّر Secrets:

- كل 3-6 شهور
- بعد أي حدث أمني
- بعد مغادرة عضو من الفريق

---

**آخر تحديث**: Nov 1, 2025  
**التوكن الحالي**: 7431625101:AAHinybqVQmZRSHN23VylqZZm_lJoi67_Wk  
**الحالة**: ✅ جاهز للتطبيق
