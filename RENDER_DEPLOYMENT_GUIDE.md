# 🚀 دليل رفع SmartEduProject على Render

---

## **📋 المتطلبات:**

1. ✅ حساب [GitHub](https://github.com)
2. ✅ حساب [Render](https://render.com) (مجاني)
3. ✅ Git مثبت على جهازك

---

## **الخطوة 1️⃣: رفع المشروع على GitHub**

### **1. إنشاء Repository على GitHub:**

1. افتح [GitHub](https://github.com/new)
2. اسم Repository: `SmartEduProject`
3. اختر **Private** أو **Public**
4. **لا تضف** README أو .gitignore (موجودين بالفعل)
5. اضغط **Create repository**

### **2. رفع الكود من Terminal:**

```bash
# افتح Terminal في مجلد المشروع
cd C:\Users\basem\OneDrive\Desktop\Basem_test_windsurf\SmartEduProject

# Initialize Git (إذا لم يكن موجود)
git init

# إضافة جميع الملفات
git add .

# Commit
git commit -m "🚀 Initial commit - SmartEduProject"

# ربط GitHub (استبدل USERNAME باسم حسابك)
git remote add origin https://github.com/USERNAME/SmartEduProject.git

# Push
git branch -M main
git push -u origin main
```

### **3. التحقق:**
- افتح Repository على GitHub
- يجب أن ترى جميع الملفات

---

## **الخطوة 2️⃣: إنشاء PostgreSQL Database على Render**

### **1. إنشاء Database:**

1. افتح [Render Dashboard](https://dashboard.render.com)
2. اضغط **New +** → **PostgreSQL**
3. املأ البيانات:
   ```
   Name: smartedu-db
   Region: Singapore (الأقرب)
   Plan: Free
   ```
4. اضغط **Create Database**

### **2. نسخ Connection String:**

1. افتح Database Details
2. انسخ **External Database URL**
3. احفظها - ستحتاجها لاحقاً

**مثال:**
```
postgresql://user:password@hostname:5432/database_name
```

---

## **الخطوة 3️⃣: نشر Backend على Render**

### **1. إنشاء Web Service:**

1. اضغط **New +** → **Web Service**
2. اختر **Connect GitHub**
3. اختر Repository: `SmartEduProject`
4. اضغط **Connect**

### **2. ملء إعدادات Service:**

```yaml
Name: smartedu-backend
Runtime: Python 3
Region: Singapore
Branch: main
Root Directory: backend
Build Command: chmod +x build.sh && ./build.sh
Start Command: gunicorn core.wsgi:application
Plan: Free
```

### **3. إضافة Environment Variables:**

اضغط **Advanced** ثم أضف:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.7` |
| `DEBUG` | `False` |
| `SECRET_KEY` | [Generate random] |
| `DATABASE_URL` | [الـ URL من Database] |
| `ALLOWED_HOSTS` | `smartedu-backend.onrender.com,localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | `https://smartedu-frontend.onrender.com` |
| `FRONTEND_URL` | `https://smartedu-frontend.onrender.com` |
| `JWT_SECRET_KEY` | [Generate random] |
| `JWT_ACCESS_TOKEN_LIFETIME` | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME` | `1440` |
| `SMTP_EMAIL` | `your-email@gmail.com` |
| `SMTP_PASSWORD` | `<your-gmail-app-password>` |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `465` |
| `TELEGRAM_BOT_TOKEN` | `YOUR_BOT_TOKEN` |
| `TELEGRAM_API_ID` | `YOUR_API_ID` |
| `TELEGRAM_API_HASH` | `YOUR_API_HASH` |
| `TELEGRAM_BOT_USERNAME` | `SmartEduProjectBot` |
| `OTP_SECRET_KEY` | [Generate random] |

### **4. نشر:**

1. اضغط **Create Web Service**
2. انتظر 5-10 دقائق للـ build
3. بعد النجاح، ستحصل على URL:
   ```
   https://smartedu-backend.onrender.com
   ```

---

## **الخطوة 4️⃣: نشر Frontend على Render**

### **الطريقة 1: Static Site (سهلة) ✅**

1. **New +** → **Static Site**
2. اختر نفس Repository
3. الإعدادات:
   ```yaml
   Name: smartedu-frontend
   Branch: main
   Root Directory: frontend
   Build Command: (leave empty)
   Publish Directory: .
   ```
4. **Create Static Site**

### **الطريقة 2: Web Service (أفضل)**

إذا تحتاج مزايا أكثر:

1. أنشئ `frontend/package.json`:
```json
{
  "name": "smartedu-frontend",
  "version": "1.0.0",
  "scripts": {
    "start": "python -m http.server 8080"
  }
}
```

2. **New +** → **Web Service**
3. الإعدادات:
   ```yaml
   Name: smartedu-frontend
   Runtime: Node
   Root Directory: frontend
   Build Command: echo "No build needed"
   Start Command: python -m http.server 8080
   ```

---

## **الخطوة 5️⃣: تحديث الروابط**

### **1. تحديث Frontend:**

في جميع ملفات JavaScript (`dashboard.js`, `join.html`, إلخ):

```javascript
// قبل:
const API_URL = 'http://localhost:8000/api';

// بعد:
const API_URL = 'https://smartedu-backend.onrender.com/api';
```

### **2. تحديث CORS في Backend:**

عد إلى Render Backend → **Environment**:

```
CORS_ALLOWED_ORIGINS=https://smartedu-frontend.onrender.com
FRONTEND_URL=https://smartedu-frontend.onrender.com
ALLOWED_HOSTS=smartedu-backend.onrender.com
```

### **3. Commit & Push:**

```bash
git add .
git commit -m "🔄 Update API URLs for production"
git push
```

Render سيعيد النشر تلقائياً!

---

## **الخطوة 6️⃣: اختبار النظام**

### **1. اختبار Backend:**

```bash
# Health Check
curl https://smartedu-backend.onrender.com/api/health/

# Login
curl -X POST https://smartedu-backend.onrender.com/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"basem902","password":"Basem@12345"}'
```

### **2. اختبار Frontend:**

1. افتح `https://smartedu-frontend.onrender.com`
2. سجل دخول
3. اختبر جميع الصفحات

---

## **⚠️ ملاحظات مهمة:**

### **Free Plan Limitations:**

| الميزة | الحد |
|--------|------|
| **Sleep after inactivity** | 15 دقيقة |
| **Cold start time** | 30-60 ثانية |
| **Bandwidth** | 100 GB/month |
| **Build minutes** | 500 minutes/month |
| **Database Storage** | 1 GB |

### **تجنب Sleep:**

**الطريقة 1: Cron Job** (خارجي)
```bash
# استخدم https://cron-job.org
GET https://smartedu-backend.onrender.com/api/health/
# كل 10 دقائق
```

**الطريقة 2: UptimeRobot** (مجاني)
1. افتح [UptimeRobot](https://uptimerobot.com)
2. أضف Monitor:
   - URL: `https://smartedu-backend.onrender.com/api/health/`
   - Interval: 5 minutes
   
---

## **🔒 الأمان:**

### **1. Secret Keys:**
```bash
# توليد Secret Key قوي:
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### **2. Environment Variables:**
- **لا تضع** secrets في الكود
- استخدم Render Environment Variables فقط

### **3. HTTPS:**
- Render يوفر HTTPS تلقائياً ✅
- استخدم `https://` دائماً

---

## **🔄 التحديثات:**

### **Auto-Deploy:**
```bash
# أي Push سيُحدّث تلقائياً
git add .
git commit -m "✨ New feature"
git push
```

### **Manual Deploy:**
1. Render Dashboard
2. اختر Service
3. اضغط **Manual Deploy** → **Deploy latest commit**

---

## **📊 Monitoring:**

### **Logs:**
1. Render Dashboard → Service
2. **Logs** tab
3. راقب الأخطاء

### **Metrics:**
1. **Metrics** tab
2. راقب:
   - CPU Usage
   - Memory
   - Response Time

---

## **🆘 استكشاف الأخطاء:**

### **Build Failed:**
```bash
# تحقق من build.sh
chmod +x backend/build.sh

# تحقق من requirements.txt
pip install -r backend/requirements.txt
```

### **Database Connection Failed:**
- تحقق من `DATABASE_URL`
- تحقق من Database status على Render

### **CORS Error:**
- تحقق من `CORS_ALLOWED_ORIGINS`
- تحقق من `ALLOWED_HOSTS`

### **Static Files Missing:**
```bash
# في build.sh
python manage.py collectstatic --no-input
```

---

## **💰 الترقية (اختياري):**

| Plan | السعر | المزايا |
|------|-------|---------|
| **Free** | $0 | 750 ساعة/شهر |
| **Starter** | $7/month | No sleep + SSL + More |
| **Standard** | $25/month | مزايا إضافية |

---

## **📞 الدعم:**

- [Render Docs](https://render.com/docs)
- [Community Forum](https://community.render.com)
- [Status Page](https://status.render.com)

---

## **✅ Checklist النشر:**

```
□ Git initialized
□ Code pushed to GitHub
□ PostgreSQL database created
□ Backend deployed
□ Frontend deployed
□ Environment variables set
□ CORS configured
□ URLs updated in code
□ SSL enabled (auto)
□ Testing completed
□ Monitoring enabled
□ Documentation updated
```

---

## **🎉 النتيجة النهائية:**

```
✅ Backend API: https://smartedu-backend.onrender.com
✅ Frontend: https://smartedu-frontend.onrender.com
✅ Database: PostgreSQL on Render
✅ HTTPS: مفعل تلقائياً
✅ Auto-Deploy: مفعل
```

**مشروعك الآن على الإنترنت! 🚀**
