# 🔐 دليل إدارة الأسرار (Secrets Management)

## ⚠️ القاعدة الذهبية

**لا ترفع أبداً أي secrets إلى Git!**

```
❌ NEVER في Git:
- API Keys
- Passwords
- Database URLs
- Bot Tokens
- Secret Keys
- Session Files

✅ ALWAYS في Secret Manager:
- Render Environment Variables
- Netlify Environment Variables
- GitHub Secrets (للـ CI/CD)
```

---

## 📋 الأسرار في المشروع

### Backend Secrets:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=465

# Telegram API
TELEGRAM_API_ID=your-api-id
TELEGRAM_API_HASH=your-api-hash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_BOT_USERNAME=YourBotUsername

# OTP & JWT
OTP_SECRET_KEY=your-otp-secret
JWT_SECRET_KEY=your-jwt-secret

# AI APIs (Optional)
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.netlify.app,https://yourdomain.com

# Frontend URL
FRONTEND_URL=https://yourdomain.netlify.app
```

### Frontend Secrets (إذا كانت موجودة):

```env
# API URLs
VITE_API_URL=https://your-backend.onrender.com
VITE_TELEGRAM_SERVICE_URL=https://your-telegram-service.onrender.com

# Feature Flags (يمكن أن تكون عامة)
VITE_ENABLE_AI=true
VITE_ENABLE_TELEGRAM=true
```

---

## 🌐 إعداد Secrets في Render

### 1️⃣ Backend Service

1. اذهب إلى: https://dashboard.render.com
2. اختر Service الخاص بالـ Backend
3. من القائمة اليسرى: **Environment**
4. أضف كل متغير على حدة:

#### الطريقة:
```
Click "Add Environment Variable"

Key: SECRET_KEY
Value: <paste your secret key>

Key: TELEGRAM_BOT_TOKEN
Value: 7431625101:AAHinybqVQmZRSHN23VylqZZm_lJoi67_Wk

Key: DATABASE_URL
Value: <auto-filled من Render Database>

... إلخ
```

#### نصائح:
- ✅ استخدم "Add from .env" لرفع دفعة واحدة
- ✅ اضغط "Save Changes" بعد الإضافة
- ✅ اعمل "Manual Deploy" لتطبيق التغييرات
- ⚠️ لا تشارك هذه القيم مع أحد

### 2️⃣ Telegram Service (إذا كان منفصلاً)

نفس الخطوات، لكن فقط أضف:
```
TELEGRAM_API_ID=your-api-id
TELEGRAM_API_HASH=your-api-hash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_BOT_USERNAME=YourBotUsername
OTP_SECRET_KEY=your-otp-secret
```

---

## 🚀 إعداد Secrets في Netlify (Frontend)

### 1️⃣ افتح Site Settings

1. اذهب إلى: https://app.netlify.com
2. اختر موقعك
3. اذهب إلى: **Site settings** > **Environment variables**

### 2️⃣ أضف المتغيرات

```
Click "Add a variable"

Key: VITE_API_URL
Value: https://your-backend.onrender.com/api

Key: VITE_TELEGRAM_SERVICE_URL
Value: https://your-telegram-service.onrender.com

... إلخ
```

### 3️⃣ أعد Deploy

- بعد إضافة المتغيرات
- اذهب إلى **Deploys**
- اضغط **Trigger deploy** > **Clear cache and deploy**

---

## 🔒 إعداد Secrets في GitHub (للـ CI/CD)

### متى تحتاجها؟
إذا كنت تستخدم GitHub Actions للـ automation

### الخطوات:

1. اذهب إلى Repository على GitHub
2. **Settings** > **Secrets and variables** > **Actions**
3. اضغط **New repository secret**
4. أضف:

```
Name: RENDER_API_KEY
Secret: <your render API key>

Name: TELEGRAM_BOT_TOKEN
Secret: <your bot token>

... إلخ
```

---

## 📁 ملفات محلية (.env)

### في مجلد backend/:

**ملف: `backend/.env`** (محمي بـ .gitignore)
```env
# نسخة محلية فقط - لا ترفع!
SECRET_KEY=local-dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=sqlite:///db.sqlite3

# أضف باقي الأسرار هنا
TELEGRAM_BOT_TOKEN=7431625101:AAHinybqVQmZRSHN23VylqZZm_lJoi67_Wk
TELEGRAM_API_ID=26671326
TELEGRAM_API_HASH=996fd0da7abec92881f41addceca3677
# ... إلخ
```

**ملف: `backend/.env.example`** (يُرفع على Git)
```env
# مثال - القيم وهمية فقط!
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

DATABASE_URL=postgresql://user:pass@host:5432/dbname

TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_API_ID=your-api-id
TELEGRAM_API_HASH=your-api-hash

# ... إلخ
```

---

## ✅ التحقق من الحماية

### 1️⃣ تحقق من .gitignore

تأكد أن `.gitignore` يحتوي على:
```gitignore
# Environment Variables
.env
.env.*
!.env.example
.env.local
.env.*.local
*.pem
*.key

# Telegram Sessions
*.session
*.session-journal
backend/sessions/
telegram_service/sessions/
```

### 2️⃣ تحقق من Git Status

قبل أي commit:
```bash
git status
```

**تأكد أن لا يظهر**:
- ❌ `.env`
- ❌ `*.session`
- ❌ أي ملف يحتوي على tokens

### 3️⃣ فحص Git History

تحقق من عدم وجود secrets في التاريخ:
```bash
git log --all --full-history --source -- **/.env
git log --all --full-history --source -- **/secrets.json
```

إذا وجدت شيء، اتبع دليل `SECURITY_FIX_GUIDE.md`

---

## 🔄 دورة الحياة الصحيحة للأسرار

### في Development (محلي):

```
1. أنشئ .env في مجلد backend/
2. أضف الأسرار المحلية
3. لا ترفعه على Git (محمي بـ .gitignore)
4. استخدمه فقط محلياً
```

### في Production (Render/Netlify):

```
1. لا ترفع .env على Git
2. أضف الأسرار في Dashboard
3. كل Service له أسراره الخاصة
4. غيّر القيم بانتظام
```

### عند التعاون:

```
1. شارك .env.example فقط (قيم وهمية)
2. كل مطور ينشئ .env الخاص به
3. لا تشارك .env الحقيقي أبداً
4. استخدم password manager للمشاركة الآمنة
```

---

## 🚨 ماذا تفعل إذا رفعت secret بالخطأ؟

### الخطوات العاجلة:

#### 1️⃣ غيّر Secret فوراً!
```
- Bot Token → @BotFather (Revoke)
- API Keys → Dashboard (Regenerate)
- Passwords → غيّرها فوراً
```

#### 2️⃣ أزل من Git History
```bash
# استخدم BFG Repo Cleaner
java -jar bfg.jar --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all
```

أو أنشئ repository جديد (الأسهل)

#### 3️⃣ أغلق GitHub Alert
```
GitHub → Security → Secret scanning alerts
→ Dismiss (بعد تغيير Secret)
```

#### 4️⃣ راقب الاستخدام
- راقب logs
- راقب billing
- ابحث عن نشاط غريب

---

## 📚 أفضل الممارسات

### ✅ افعل:

1. **استخدم Environment Variables**
   - Render → Environment
   - Netlify → Environment variables
   - Local → .env (غير مرفوع)

2. **استخدم Secret Managers**
   - AWS Secrets Manager
   - Google Cloud Secret Manager
   - HashiCorp Vault
   - 1Password/Bitwarden (للتعاون)

3. **دوّر الأسرار بانتظام**
   - كل 3-6 شهور
   - بعد مغادرة عضو من الفريق
   - بعد أي خرق أمني

4. **استخدم قيم مختلفة**
   - Development ≠ Production
   - كل بيئة لها أسرارها

### ❌ لا تفعل:

1. **لا ترفع secrets على Git**
   - حتى لو private repo
   - Git history يبقى للأبد

2. **لا تشارك secrets في**
   - Slack/Teams/Discord
   - Email
   - Screenshots
   - Documentation عامة

3. **لا تستخدم secrets في**
   - Frontend code (يظهر للمستخدم)
   - URLs (تظهر في logs)
   - Error messages

4. **لا تترك secrets**
   - Hard-coded في الكود
   - في comments
   - في console.log()

---

## 🧪 اختبار الحماية

### Checklist:

```
[ ] .env محمي بـ .gitignore
[ ] .env.example موجود (قيم وهمية)
[ ] git status لا يظهر .env
[ ] Render Environment Variables محدّثة
[ ] Netlify Environment Variables محدّثة
[ ] GitHub Alerts مغلقة (بعد الإصلاح)
[ ] تم تدوير Secrets المكشوفة
[ ] Production تستخدم secrets مختلفة عن Development
[ ] لا secrets في Frontend code
[ ] لا sessions files مرفوعة
```

---

## 🔗 روابط مفيدة

### Documentation:
- Render Environment Variables: https://render.com/docs/environment-variables
- Netlify Environment Variables: https://docs.netlify.com/environment-variables/overview/
- GitHub Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets

### Tools:
- git-secrets: https://github.com/awslabs/git-secrets
- BFG Repo Cleaner: https://rtyley.github.io/bfg-repo-cleaner/
- TruffleHog: https://github.com/trufflesecurity/trufflehog

### Security Scanners:
- GitHub Secret Scanning: مدمج
- GitGuardian: https://www.gitguardian.com/
- Snyk: https://snyk.io/

---

## 📞 الدعم

إذا احتجت مساعدة:
1. راجع `SECURITY_FIX_GUIDE.md`
2. راجع `HOW_TO_CLOSE_GITHUB_ALERT.md`
3. أخبرني إذا واجهت مشكلة!

---

**آخر تحديث**: Nov 1, 2025  
**الحالة**: ✅ .gitignore محدّث، Secrets محمية  
**التالي**: تطبيق Secrets في Render/Netlify Dashboards
