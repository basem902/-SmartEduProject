# 📤 دليل رفع المشروع على GitHub

هذا الدليل يشرح الخطوات الكاملة لرفع المشروع على GitHub بأمان.

---

## ✅ تم إعداده مسبقاً

- ✓ `.gitignore` - يمنع رفع ملفات حساسة
- ✓ `.env.example` - نموذج بدون أسرار
- ✓ `README.md` - وثائق المشروع
- ✓ `DEPLOYMENT.md` - دليل النشر
- ✓ تنقيح جميع الأسرار من الملفات

---

## 🚀 الخطوات (نفذها بالترتيب)

### 1. تأكد من وجود Git
```powershell
git --version
```
إن لم يكن مثبتاً، حمّله من: https://git-scm.com/download/win

---

### 2. افتح PowerShell في مجلد المشروع
```powershell
cd "c:\Users\basem\OneDrive\Desktop\Basem_test_windsurf\SmartEduProject"
```

---

### 3. تهيئة Git
```powershell
# إنشاء Git Repository
git init

# إعداد اسمك والإيميل (مرة واحدة فقط)
git config --global user.name "basem"
git config --global user.email "your-email@example.com"
```

---

### 4. مراجعة الملفات
```powershell
# عرض جميع الملفات (تأكد أن .env لن يُرفع)
git status
```

⚠️ **مهم جداً**: تأكد أن `backend/.env` غير موجود في القائمة!

---

### 5. إضافة الملفات للتتبع
```powershell
# إضافة جميع الملفات
git add .

# مراجعة ما تم إضافته
git status
```

---

### 6. أول Commit
```powershell
git commit -m "Initial commit: SmartEdu Project - Backend + Frontend + Telegram Integration"
```

---

### 7. إنشاء مستودع GitHub

#### عبر الموقع:
1. اذهب إلى: https://github.com/new
2. اسم المستودع: `SmartEduProject`
3. الوصف: "Smart Educational Project Management System with Telegram Integration"
4. اختر: **Public** ✅
5. **لا تضف** README أو .gitignore (موجودين بالفعل)
6. اضغط "Create repository"

---

### 8. ربط المستودع المحلي بـ GitHub
```powershell
# غيّر YOUR_USERNAME باسمك على GitHub
git remote add origin https://github.com/YOUR_USERNAME/SmartEduProject.git

# تأكد من الربط
git remote -v
```

---

### 9. تسمية الفرع الرئيسي
```powershell
git branch -M main
```

---

### 10. دفع الكود إلى GitHub
```powershell
# أول دفع (سيطلب منك GitHub credentials)
git push -u origin main
```

#### إذا طُلِب منك تسجيل الدخول:
- سيُفتح متصفح تلقائياً
- سجّل دخول GitHub
- اسمح للوصول

---

## ✅ التحقق من النجاح

1. افتح: `https://github.com/YOUR_USERNAME/SmartEduProject`
2. تأكد من وجود جميع الملفات
3. **تحقق**: backend/.env غير موجود ✅
4. **تحقق**: .env.example موجود ✅

---

## 🔐 ما بعد الرفع - حماية الأسرار

### 1. إضافة GitHub Secrets (للـ CI/CD مستقبلاً)
1. افتح Repository → Settings → Secrets and variables → Actions
2. اضغط "New repository secret"
3. أضف واحداً تلو الآخر:

```
SECRET_KEY=<your-django-secret-key>
DATABASE_URL=<your-database-url>
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_API_ID=<your-api-id>
TELEGRAM_API_HASH=<your-api-hash>
OTP_SECRET_KEY=<your-otp-secret>
JWT_SECRET_KEY=<your-jwt-secret>
SMTP_EMAIL=<your-email>
SMTP_PASSWORD=<your-smtp-password>
GEMINI_API_KEY=<your-gemini-key>
```

---

### 2. تدوير (تغيير) جميع المفاتيح

⚠️ **مهم جداً**: بعد الرفع، غيّر:
- ✓ SECRET_KEY في Django
- ✓ TELEGRAM_BOT_TOKEN (أنشئ bot جديد)
- ✓ SMTP_PASSWORD (أنشئ App Password جديد)
- ✓ OTP_SECRET_KEY
- ✓ JWT_SECRET_KEY
- ✓ كلمة مرور قاعدة البيانات

**السبب**: احتياطاً إن كانت القيم القديمة تسربت في commits سابقة.

---

## 🔄 التحديثات المستقبلية

عند تعديل الكود:

```powershell
# مراجعة التغييرات
git status

# إضافة التعديلات
git add .

# Commit مع وصف واضح
git commit -m "وصف التعديلات"

# دفع للـ GitHub
git push
```

---

## 📊 فروع Git (اختياري)

### إنشاء فرع للتطوير:
```powershell
# إنشاء والانتقال لفرع dev
git checkout -b dev

# دفع الفرع لـ GitHub
git push -u origin dev
```

### دمج الفروع:
```powershell
# العودة لـ main
git checkout main

# دمج dev في main
git merge dev

# دفع التحديثات
git push
```

---

## 🛡️ حماية الفرع الرئيسي

1. Repository → Settings → Branches
2. اضغط "Add rule"
3. Branch name pattern: `main`
4. فعّل:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass

---

## 🔍 فحص الأسرار (اختياري)

### تثبيت gitleaks:
```powershell
# عبر Chocolatey (إن كان مثبتاً)
choco install gitleaks

# أو حمّل من: https://github.com/gitleaks/gitleaks/releases
```

### فحص المشروع:
```powershell
gitleaks detect --source . --verbose
```

---

## ❌ حل المشاكل

### خطأ: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/SmartEduProject.git
```

### خطأ: "failed to push"
```powershell
# سحب التحديثات أولاً
git pull origin main --rebase
git push
```

### خطأ: "Authentication failed"
- استخدم Personal Access Token بدلاً من كلمة المرور
- Settings → Developer settings → Personal access tokens → Generate new token

---

## 📚 موارد إضافية

- [GitHub Docs](https://docs.github.com)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Protecting Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## ⚠️ تذكير نهائي

**لا ترفع أبداً**:
- ❌ ملف `.env`
- ❌ Tokens أو API Keys
- ❌ كلمات المرور
- ❌ بيانات شخصية
- ❌ ملفات التشغيل الكبيرة

**تأكد دائماً**:
- ✅ `.gitignore` محدّث
- ✅ مراجعة `git status` قبل commit
- ✅ استخدام `.env.example` للقيم النموذجية

---

**تم الإعداد**: أكتوبر 2025  
**آخر مراجعة**: قبل الرفع مباشرة ✅
