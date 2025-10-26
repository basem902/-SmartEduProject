# 📚 SmartEdu - نظام إدارة المشاريع التعليمية

نظام متكامل لإدارة المشاريع الدراسية مع تكامل Telegram للإشعارات والتسليمات.

## ✨ المميزات الرئيسية

- 🎓 **إدارة المشاريع**: إنشاء وإدارة المشاريع الدراسية بسهولة
- 📱 **تكامل Telegram**: إشعارات تلقائية وتسليمات عبر البوت
- 🔐 **نظام مصادقة آمن**: JWT + OTP عبر Email/Telegram
- 👥 **إدارة الشُعب**: تنظيم الطلاب في شعب ومجموعات
- 📊 **لوحة تحكم**: واجهة حديثة ومتجاوبة
- 🤖 **ذكاء اصطناعي**: تكامل Gemini AI لتوليد المحتوى
- 📂 **رفع الملفات**: دعم متعدد لأنواع الملفات
- 🌙 **الوضع الداكن**: يتبع تفضيلات النظام
- 📱 **PWA**: يعمل كتطبيق على الأجهزة المحمولة

---

## 🚀 التشغيل السريع (محلياً)

### المتطلبات
- Python 3.11+
- PostgreSQL أو SQLite
- حساب Telegram Bot

### 1. استنساخ المشروع
```bash
git clone https://github.com/YOUR_USERNAME/SmartEduProject.git
cd SmartEduProject
```

### 2. إعداد Backend
```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# تثبيت المتطلبات
pip install -r requirements.txt

# نسخ ملف البيئة
cp ../.env.example .env
# حرّر .env وأدخل قيمك الحقيقية

# تطبيق Migrations
python manage.py migrate

# إنشاء superuser
python manage.py createsuperuser

# تشغيل السيرفر
python -m daphne -b 127.0.0.1 -p 8000 core.asgi:application
```

### 3. إعداد Frontend
```bash
# في نافذة جديدة
cd frontend

# استخدم Live Server أو أي web server
# مثلاً باستخدام VS Code Live Server على المنفذ 5500
```

### 4. إعداد Telegram Bot (اختياري)
```bash
cd telegram_bot

# حرّر .env وأضف TELEGRAM_BOT_TOKEN
python bot.py
```

---

## 📁 هيكل المشروع

```
SmartEduProject/
├── backend/               # Django Backend
│   ├── apps/
│   │   ├── accounts/     # نظام المصادقة
│   │   ├── projects/     # إدارة المشاريع
│   │   ├── sections/     # إدارة الشُعب
│   │   └── submissions/  # التسليمات
│   ├── core/             # الإعدادات الرئيسية
│   └── manage.py
├── frontend/             # HTML/CSS/JS Frontend
│   ├── pages/           # صفحات التطبيق
│   ├── assets/          # CSS/JS/Images
│   └── manifest.json    # PWA Config
├── telegram_bot/        # Telegram Bot
│   └── bot.py
├── .env.example         # نموذج متغيرات البيئة
├── .gitignore          # ملفات Git المستثناة
├── DEPLOYMENT.md       # دليل النشر على Render
└── README.md           # هذا الملف
```

---

## 🔐 الأمان

- ✅ جميع الأسرار في `.env` (مستثنى من Git)
- ✅ HTTPS في الإنتاج
- ✅ CORS محدودة
- ✅ JWT للمصادقة
- ✅ OTP ثنائي العامل
- ✅ فحص ملفات (ClamAV اختياري)

---

## 🌐 النشر على الإنتاج

راجع [DEPLOYMENT.md](./DEPLOYMENT.md) للخطوات الكاملة لنشر المشروع على:
- Backend: Render
- Frontend: Cloudflare Pages
- Database: Supabase

---

## 🛠️ التقنيات المستخدمة

### Backend:
- Django 5.x
- Django Channels (WebSocket)
- Django REST Framework
- PostgreSQL / SQLite
- JWT Authentication

### Frontend:
- Vanilla HTML/CSS/JavaScript
- PWA (Service Worker)
- Responsive Design
- Dark Mode Support

### Integrations:
- Telegram Bot API
- Gemini AI
- Gmail SMTP
- Supabase

---

## 📖 الوثائق

- [دليل النشر](./DEPLOYMENT.md)
- [دليل إعداد Telegram](./TELEGRAM_AUTO_SETUP_INSTRUCTIONS.md)
- [حل المشاكل](./SOLUTION_FINAL.md)

---

## 🤝 المساهمة

المساهمات مرحب بها! الرجاء:
1. Fork المشروع
2. أنشئ فرع للميزة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add AmazingFeature'`)
4. Push للفرع (`git push origin feature/AmazingFeature`)
5. افتح Pull Request

---

## ⚠️ ملاحظات مهمة

1. **لا ترفع ملف `.env` أبداً**
2. دوّر جميع المفاتيح السرية بعد الاستنساخ
3. استخدم `.env.example` كنموذج فقط
4. فعّل 2FA على جميع حساباتك

---

## 📞 التواصل

للأسئلة أو الدعم، افتح Issue في GitHub.

---

## 📄 الترخيص

هذا المشروع للأغراض التعليمية. استخدمه بمسؤولية.

---

**تم الإنشاء بواسطة**: فريق SmartEdu  
**آخر تحديث**: أكتوبر 2025
