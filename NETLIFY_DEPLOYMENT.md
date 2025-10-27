# 🌐 دليل نشر Frontend على Netlify

## ✅ التحضيرات المكتملة:

### 1. تحديث API URLs
- ✅ `config.js` - Auto-detection للبيئة
- ✅ Development: `http://localhost:8000/api`
- ✅ Production: `https://smarteduproject-k0um.onrender.com/api`

### 2. ملفات Netlify
- ✅ `netlify.toml` - إعدادات البناء
- ✅ `_redirects` - توجيه الطلبات

---

## 🚀 طريقة النشر:

### الطريقة 1: Drag & Drop (الأسهل)

1. افتح https://app.netlify.com/
2. سجل دخول (أو أنشئ حساب)
3. اضغط **"Add new site"** → **"Deploy manually"**
4. اسحب مجلد `frontend` كاملاً
5. انتظر 2-3 دقائق
6. احصل على الرابط: `https://yoursite.netlify.app`

---

### الطريقة 2: GitHub Integration (الأفضل)

#### الخطوة 1: Push إلى GitHub
```bash
git add .
git commit -m "Prepare for Netlify deployment"
git push origin main
```

#### الخطوة 2: ربط Netlify بـ GitHub

1. افتح https://app.netlify.com/
2. اضغط **"Add new site"** → **"Import from Git"**
3. اختر **GitHub**
4. اختر Repository: `SmartEduProject`

#### الخطوة 3: إعدادات البناء

```
Base directory:     frontend
Publish directory:  frontend
Build command:      (leave empty)
```

#### الخطوة 4: Deploy

اضغط **"Deploy site"** وانتظر 2-3 دقائق

---

## 🎯 بعد النشر:

### 1. اختبار الصفحات:
- ✅ `/pages/login.html`
- ✅ `/pages/dashboard.html`
- ✅ `/pages/sections-setup.html`
- ✅ `/pages/create-project.html`
- ✅ `/join/basem902`

### 2. اختبار APIs:
- افتح Console (F12)
- تحقق من: `environment: "Production"`
- تحقق من: `API_BASE` يشير للـ Backend

### 3. Custom Domain (اختياري):
- Site settings → Domain management
- غيّر إلى: `smartedu-yourname.netlify.app`

---

## 📱 PWA Support:

التطبيق يدعم PWA تلقائياً:
- ✅ `manifest.json`
- ✅ Service Worker
- ✅ Icons (192x192, 512x512)
- ✅ Offline Support

---

## 🔧 إعادة النشر:

### Auto Deploy (GitHub Integration):
```bash
git add .
git commit -m "Update frontend"
git push origin main
```
**Netlify ينشر تلقائياً خلال 2-3 دقائق!**

### Manual Deploy:
1. افتح Netlify Dashboard
2. اذهب لـ Site
3. اضغط **"Deploys"** → **"Trigger deploy"**

---

## 📊 URLs:

```
Frontend:  https://yoursite.netlify.app
Backend:   https://smarteduproject-k0um.onrender.com
Admin:     https://smarteduproject-k0um.onrender.com/admin/
```

---

## ✅ Checklist:

- [ ] Push code to GitHub
- [ ] Create Netlify account
- [ ] Import from GitHub
- [ ] Configure build settings
- [ ] Deploy site
- [ ] Test all pages
- [ ] Test API calls
- [ ] Set custom domain (optional)
- [ ] Enable HTTPS (automatic)
- [ ] Test PWA features

---

## 🎉 Done!

Frontend منشور وجاهز للاستخدام!
