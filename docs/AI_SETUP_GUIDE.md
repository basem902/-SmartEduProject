# 🤖 دليل إعداد نظام AI لاستلام المشاريع

## 📋 الخطوات المكتملة ✅

- [x] إعداد Celery
- [x] تحديث Settings
- [x] إضافة Redis Configuration
- [x] تحديث Requirements
- [x] إنشاء ملفات الاختبار

---

## 🚀 الخطوات التالية

### 1️⃣ إنشاء Upstash Redis Database

**اذهب إلى:** https://upstash.com/

1. **Sign Up** باستخدام GitHub
2. **Create Database**:
   - Name: `smartedu-redis`
   - Type: `Regional`
   - Region: `EU-Central-1` أو أقرب منطقة
3. **انسخ Redis URL** من صفحة Database

### 2️⃣ تحديث ملف `.env`

أضف Redis URL:

```bash
REDIS_URL=rediss://default:AbC123@us1-xxx.upstash.io:6379
CELERY_BROKER_URL=rediss://default:AbC123@us1-xxx.upstash.io:6379
CELERY_RESULT_BACKEND=rediss://default:AbC123@us1-xxx.upstash.io:6379
```

### 3️⃣ اختبار الاتصال

```bash
cd backend
python test_redis_connection.py
```

**النتيجة المتوقعة:**
```
✅ Redis يعمل بشكل صحيح!
```

### 4️⃣ تشغيل Celery Worker

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A config worker --loglevel=info --pool=solo
```

---

## 📊 الميزات التي سيتم إضافتها

### المرحلة 1: Models + API ✅✅✅
- [x] تحديث Project Model
- [x] تحديث Submission Model
- [x] إنشاء API Endpoint للرفع
- [x] إنشاء Celery Task
- [x] إنشاء Notifications System
- [x] إضافة URLs

### المرحلة 2: AI Validator
- [ ] إنشاء AIValidator Class
- [ ] معالجة الفيديو
- [ ] OCR للنصوص
- [ ] تحليل المحتوى بـ Gemini
- [ ] كشف التشابه

### المرحلة 3: الإشعارات
- [ ] إشعار القبول
- [ ] إشعار الرفض
- [ ] إشعار المعلم (تشابه عالي)

### المرحلة 4: Frontend
- [ ] تحديث submit-project.js
- [ ] إضافة Progress Bar
- [ ] عرض النتائج

---

## 🧪 الاختبار

```bash
# اختبار Redis
python test_redis_connection.py

# اختبار Celery
python manage.py shell
>>> from config.celery import app
>>> app.control.ping()

# اختبار AI
python test_ai_validation.py
```

---

## 📞 الدعم

إذا واجهت مشاكل:
1. تأكد من Redis URL في `.env`
2. تأكد من تثبيت المكتبات
3. تحقق من الـ logs

---

## 🎯 الخطوة التالية

بعد إعداد Redis، ابدأ في **المرحلة 1: تحديث Models**
