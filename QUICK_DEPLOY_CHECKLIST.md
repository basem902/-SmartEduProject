# ✅ Checklist سريع للـ Deploy

## 🎯 قبل Deploy على Render

### 1. التحقق من الملفات المحلية

```bash
# تأكد أن .env غير مرفوع
git status

# يجب ألا يظهر:
# ❌ .env
# ❌ *.session
# ❌ *_INSTRUCTIONS.txt
```

### 2. تحديث .env.example

- [ ] جميع المتغيرات موجودة
- [ ] جميع القيم وهمية (placeholders)
- [ ] لا توكنات حقيقية

### 3. Commit التغييرات

```bash
git add .
git commit -m "security: Update secrets management"
git push origin main
```

---

## 🚀 Deploy على Render

### Backend Service

#### Environment Variables:
```
SECRET_KEY=<generate-random>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=<auto-filled>
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_API_ID=<your-api-id>
TELEGRAM_API_HASH=<your-api-hash>
TELEGRAM_BOT_USERNAME=YourBotUsername
OTP_SECRET_KEY=<generate-random>
JWT_SECRET_KEY=<generate-random>
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=<your-app-password>
CORS_ALLOWED_ORIGINS=https://smartedu-basem.netlify.app
FRONTEND_URL=https://smartedu-basem.netlify.app
```

#### الخطوات:
- [ ] 1. افتح https://dashboard.render.com
- [ ] 2. اختر Backend Service
- [ ] 3. Environment → Add/Update variables
- [ ] 4. Save Changes
- [ ] 5. Manual Deploy
- [ ] 6. انتظر 2-3 دقائق
- [ ] 7. افحص Logs (لا أخطاء)

---

## 🌐 Deploy على Netlify

### Frontend

#### Environment Variables:
```
VITE_API_URL=https://your-backend.onrender.com/api
VITE_TELEGRAM_SERVICE_URL=https://your-telegram-service.onrender.com
VITE_ENABLE_TELEGRAM=true
```

#### الخطوات:
- [ ] 1. افتح https://app.netlify.com
- [ ] 2. اختر Site
- [ ] 3. Site settings → Environment variables
- [ ] 4. Add variables
- [ ] 5. Deploys → Trigger deploy → Clear cache and deploy
- [ ] 6. انتظر 1-2 دقيقة
- [ ] 7. افحص Site (يعمل بدون أخطاء)

---

## 🧪 الاختبار

### Backend Test:
```
1. افتح: https://your-backend.onrender.com/api/
2. يجب أن يظهر: API documentation أو welcome message
3. لا "Internal Server Error"
```

### Frontend Test:
```
1. افتح: https://smartedu-basem.netlify.app
2. الصفحة تحمّل بشكل كامل
3. لا أخطاء في Console (F12)
```

### Telegram Test:
```
1. جرّب ربط حساب Telegram
2. أدخل رقم هاتف
3. يجب أن يُرسل الكود ✅
```

---

## 🔒 الأمان

### تحقق من:
- [ ] لا .env مرفوع على Git
- [ ] GitHub Security Alerts مغلقة
- [ ] Render Secrets محدّثة
- [ ] Netlify Secrets محدّثة
- [ ] Production يستخدم tokens مختلفة عن Development

---

## 🗑️ التنظيف

### احذف الملفات المؤقتة:
```bash
del UPDATE_TOKEN_INSTRUCTIONS.txt
del TELEGRAM_CODE_SEARCH_GUIDE.md
```

### احتفظ بـ:
- ✅ SECRETS_MANAGEMENT_GUIDE.md
- ✅ RENDER_SECRETS_SETUP.md
- ✅ SECURITY_FIX_GUIDE.md
- ✅ HOW_TO_CLOSE_GITHUB_ALERT.md

---

## 📊 Monitoring

### بعد Deploy:
- [ ] راقب Logs على Render (أول ساعة)
- [ ] راقب استخدام Database
- [ ] تحقق من عمل جميع Features
- [ ] اختبر من أجهزة مختلفة

---

## 🔄 الصيانة الدورية

### كل شهر:
- [ ] راجع Logs
- [ ] راجع استخدام الموارد
- [ ] احذف Logs القديمة

### كل 3-6 شهور:
- [ ] دوّر Secrets (غيّر Tokens)
- [ ] حدّث Dependencies
- [ ] راجع Security Alerts

---

**آخر تحديث**: Nov 1, 2025  
**الحالة**: ✅ جاهز للـ Deploy
