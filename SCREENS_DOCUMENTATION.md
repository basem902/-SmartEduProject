# 📱 دليل شامل لشاشات SmartEdu Project

## جدول جميع شاشات HTML في المشروع

| # | اسم الشاشة | الخدمات/الوظائف | JavaScript المرتبط | النوع | المسار |
|---|------------|------------------|-------------------|-------|--------|
| 1 | **الصفحة الرئيسية** | عرض المنصة، التعريف بالميزات، روابط التسجيل والدخول | api.js, ui.js, theme.js, auth.js, app.js | User | `/frontend/index.html` |
| 2 | **تسجيل الدخول** | تسجيل دخول المعلمين، إظهار/إخفاء كلمة المرور، تذكرني | api.js, ui.js, theme.js, auth.js, app.js | User | `/frontend/pages/login.html` |
| 3 | **التسجيل** | تسجيل معلم جديد، إرسال كود التفعيل، تفعيل الحساب، كشف تلقائي للكود | api.js, ui.js, theme.js, auth.js, app.js | User | `/frontend/pages/register.html` |
| 4 | **لوحة التحكم** | عرض إحصائيات المشاريع والطلاب والشُعب، إجراءات سريعة، قائمة المشاريع الحديثة | api.js, ui.js, theme.js, auth.js, app.js, sections-api.js | User | `/frontend/pages/dashboard.html` |
| 5 | **إنشاء مشروع** | Wizard 6 خطوات، توليد محتوى AI، اختيار الشُعب، رفع ملفات، إعدادات التسليم | create-project.js | User | `/frontend/pages/create-project.html` |
| 6 | **رفع مشروع** | 4 خطوات: معلومات الطالب، OTP، رفع ملف، نتيجة | api-config.js, submit-project.js | User | `/frontend/pages/submit-project.html` |
| 7 | **الإعدادات** | تغيير كلمة المرور، تفضيلات (Theme, Language), روابط سريعة، حذف الحساب | api.js, ui.js, theme.js, auth.js, app.js | User | `/frontend/pages/settings.html` |
| 8 | **إعداد الصفوف** | إنشاء صف جديد، 5 خطوات: مرحلة، صف، عدد شُعب، روابط، مراجعة | api.js, ui.js, auth.js, theme.js, app.js, sections-api.js | User | `/frontend/pages/sections-setup.html` |
| 9 | **إدارة الشُعب** | عرض الصفوف، تفاصيل الشُعب، قائمة الطلاب، نسخ الروابط، تصدير CSV/Excel | api.js, ui.js, auth.js, theme.js, app.js, sections-api.js | User | `/frontend/pages/sections-manage.html` |
| 10 | **إحصائيات الشُعب** | نظرة عامة، توزيع المراحل، أفضل 10 شُعب، النشاط الأخير، تصدير CSV | api.js, ui.js, auth.js, theme.js, app.js, sections-api.js | User | `/frontend/pages/sections-dashboard.html` |
| 11 | **انضمام الطلاب** | 3 شاشات: ترحيب، تسجيل، نجاح + روابط القروبات، Confetti | api.js, ui.js, theme.js, app.js, sections-api.js | User | `/frontend/pages/join.html` |
| 12 | **مركز الاختبارات** | قائمة صفحات الاختبار، فحص حالة Backend، روابط سريعة | Inline JavaScript | Testing | `/frontend/pages/testing-index.html` |
| 13 | **اختبار OTP** | 3 اختبارات: توليد OTP، التحقق، رفع ملف + إحصائيات وسجل | Inline JavaScript | Testing | `/frontend/pages/otp-test.html` |
| 14 | **اختبار البوت** | دليل اختبار Telegram Bot، خطوات، أوامر، سيناريوهات، حل المشاكل | Inline JavaScript | Testing | `/frontend/pages/bot-test.html` |
| 15 | **توليد Payload** | توليد Payload وهمي للاختبار، نسخ للحافظة | Inline JavaScript | Testing | `/frontend/pages/payload-generator.html` |
| 16 | **تسجيل دخول سريع** | تسجيل دخول سريع بحساب افتراضي للتطوير | Inline JavaScript | Testing | `/frontend/pages/quick-login.html` |
| 17 | **لا يوجد اتصال** | صفحة Offline للـ PWA، كشف عودة الاتصال | Inline JavaScript | Utility | `/frontend/pages/offline.html` |
| 18 | **مسح Cache** | حذف Service Worker و Cache، إعادة التحميل | Inline JavaScript | Utility | `/frontend/clear-cache.html` |
| 19 | **تسجيل دخول المدير** | تسجيل دخول للمديرين فقط (Superuser) | admin-auth.js | Admin | `/frontend/admin/index.html` |
| 20 | **لوحة المدير** | نظرة عامة على الجداول، إحصائيات، حذف البيانات | admin-auth.js, admin-api.js, admin-dashboard.js | Admin | `/frontend/admin/dashboard.html` |
| 21 | **عرض الجدول** | عرض بيانات جدول، بحث، فلترة، حذف سجلات، تصدير CSV/JSON | admin-auth.js, admin-api.js | Admin | `/frontend/admin/table-viewer.html` |

---

## 📊 الإحصائيات الإجمالية

- **إجمالي الشاشات**: 21 شاشة HTML
- **شاشات المستخدم (User)**: 11 شاشة
- **شاشات الاختبار (Testing)**: 5 شاشات
- **شاشات الإدارة (Admin)**: 3 شاشات
- **شاشات مساعدة (Utility)**: 2 شاشة

---

## 🎯 تصنيف الشاشات حسب النوع

### 👤 User Screens (11 شاشة)

#### Authentication & Profile
1. **index.html** - الصفحة الرئيسية
2. **login.html** - تسجيل الدخول
3. **register.html** - التسجيل والتفعيل
4. **settings.html** - الإعدادات

#### Dashboard & Projects
5. **dashboard.html** - لوحة التحكم الرئيسية
6. **create-project.html** - إنشاء مشروع جديد
7. **submit-project.html** - رفع مشروع (للطلاب)

#### Sections Management
8. **sections-setup.html** - إعداد صفوف وشُعب جديدة
9. **sections-manage.html** - إدارة الصفوف والشُعب
10. **sections-dashboard.html** - إحصائيات وتقارير الشُعب
11. **join.html** - صفحة انضمام الطلاب

### 🧪 Testing Screens (5 شاشات)

1. **testing-index.html** - مركز الاختبارات الرئيسي
2. **otp-test.html** - اختبار نظام OTP كامل
3. **bot-test.html** - دليل اختبار Telegram Bot
4. **payload-generator.html** - توليد Payload للاختبار
5. **quick-login.html** - تسجيل دخول سريع للتطوير

### 👨‍💼 Admin Screens (3 شاشات)

1. **admin/index.html** - تسجيل دخول المدير
2. **admin/dashboard.html** - لوحة تحكم قاعدة البيانات
3. **admin/table-viewer.html** - عرض وإدارة الجداول

### ⚙️ Utility Screens (2 شاشة)

1. **offline.html** - صفحة عدم الاتصال (PWA)
2. **clear-cache.html** - أداة مسح الكاش

---

## 🔧 ملفات JavaScript الرئيسية

### Core Scripts (مشتركة)
- **api.js** - إدارة استدعاءات API
- **ui.js** - وظائف واجهة المستخدم
- **auth.js** - نظام المصادقة
- **theme.js** - إدارة الوضع الليلي
- **app.js** - وظائف التطبيق الأساسية

### Specialized Scripts
- **create-project.js** - منطق صفحة إنشاء المشروع
- **submit-project.js** - منطق رفع المشروع
- **sections-api.js** - API خاصة بنظام الشُعب
- **admin-auth.js** - مصادقة المديرين
- **admin-api.js** - API لوحة المدير
- **admin-dashboard.js** - منطق لوحة المدير

---

## 🎨 الميزات المشتركة

جميع الشاشات تدعم:
- ✅ **Dark Mode** - الوضع الليلي
- ✅ **Responsive Design** - تصميم متجاوب
- ✅ **PWA Support** - دعم تطبيقات الويب التقدمية
- ✅ **RTL** - الدعم الكامل للعربية
- ✅ **Animations** - رسوم متحركة سلسة
- ✅ **Security** - حماية متقدمة

---

## 🚀 روابط الوصول السريع

### للمستخدمين:
- الصفحة الرئيسية: `http://localhost:5500/`
- تسجيل الدخول: `http://localhost:5500/pages/login.html`
- لوحة التحكم: `http://localhost:5500/pages/dashboard.html`
- إنشاء مشروع: `http://localhost:5500/pages/create-project.html`

### للمطورين:
- مركز الاختبارات: `http://localhost:5500/pages/testing-index.html`
- تسجيل دخول سريع: `http://localhost:5500/pages/quick-login.html`

### للمديرين:
- لوحة الإدارة: `http://localhost:5500/admin/`

### الحساب الافتراضي:
```
Username: basem902
Password: Basem@12345
```

---

## 📝 ملاحظات مهمة

1. **Backend Required**: معظم الشاشات تحتاج Backend يعمل على `http://localhost:8000`
2. **Database**: تحتاج قاعدة بيانات مُهيأة ومشغلة
3. **Telegram Bot**: بعض الوظائف تحتاج Telegram Bot نشط
4. **Live Server**: استخدم Live Server على port 5500 للـ Frontend

---

**آخر تحديث**: 19 أكتوبر 2025

**الحالة**: ✅ جاهز للاستخدام
