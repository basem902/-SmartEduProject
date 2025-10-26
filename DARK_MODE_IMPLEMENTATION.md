# 🌙 دليل تطبيق Dark Mode System

## ✅ تم الإنجاز

### 1. **الملفات المُنشأة:**

```
✅ assets/js/dark-mode-manager.js   - النظام الأساسي
✅ assets/js/dark-mode-init.js      - ملف التهيئة السريع
```

### 2. **الصفحات المُحدّثة:**

```
✅ pages/login.html                 - تم إضافة Dark Mode
```

---

## 📝 كيفية إضافة Dark Mode لأي صفحة

### الطريقة 1: استخدام dark-mode-init.js (سريعة)

**أضف قبل إغلاق `</body>`:**

```html
<!-- Dark Mode System -->
<script src="/assets/js/dark-mode-manager.js"></script>
<script src="/assets/js/dark-mode-init.js"></script>
```

**وأضف data attribute للـ body:**

```html
<body data-page-type="dashboard">
<!-- أو -->
<body data-page-type="auth">
<!-- أو -->
<body data-page-type="wizard">
</body>
```

**أنواع الصفحات:**
- `auth` - login, register (زر في top-left)
- `dashboard` - لوحات التحكم (زر في top-right, small)
- `wizard` - sections-setup, create-project (زر في bottom-left, small)
- `default` - باقي الصفحات (زر في top-right)

---

### الطريقة 2: تخصيص كامل

```html
<!-- Dark Mode System -->
<script src="/assets/js/dark-mode-manager.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', () => {
        // إنشاء زر مخصص
        darkModeManager.createToggle(null, {
            position: 'top-right',  // top-right, top-left, bottom-right, bottom-left
            size: 'medium',         // small, medium, large
            showLabel: false,       // إظهار نص "الوضع الداكن"
            customClass: 'my-custom-class'
        });
        
        // أو التحكم البرمجي:
        // darkModeManager.enable();   // تفعيل
        // darkModeManager.disable();  // تعطيل
        // darkModeManager.toggle();   // تبديل
    });
</script>
</body>
```

---

### الطريقة 3: زر مخصص موجود

إذا كان لديك زر موجود في الصفحة:

```html
<button id="myDarkModeBtn">🌙</button>

<script src="/assets/js/dark-mode-manager.js"></script>
<script>
    document.getElementById('myDarkModeBtn').addEventListener('click', () => {
        darkModeManager.toggle();
    });
    
    // الاستماع للتغييرات
    window.addEventListener('darkmodechange', (e) => {
        console.log('Dark mode changed:', e.detail.isDark);
        // تحديث UI الخاص بك
    });
</script>
```

---

## 🎨 CSS المطلوب

تأكد من وجود متغيرات CSS هذه في `dark-mode.css`:

```css
/* Light Mode (Default) */
:root {
    --bg-color: #ffffff;
    --bg-card: #f8f9fa;
    --text-primary: #333333;
    --text-secondary: #666666;
    --border-color: #e0e0e0;
}

/* Dark Mode */
body.dark-mode {
    --bg-color: #1a1a2e;
    --bg-card: #2d2d3d;
    --text-primary: #ffffff;
    --text-secondary: #b0b0b0;
    --border-color: #444444;
    
    background-color: var(--bg-color);
    color: var(--text-primary);
}

/* تطبيق على العناصر */
.card {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

input, select, textarea {
    background: var(--bg-color);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

/* ... إلخ */
```

---

## 📋 قائمة الصفحات - حالة التطبيق

### ✅ تم التطبيق:
- [x] login.html

### 📝 المطلوب تطبيقه:

#### صفحات أساسية (أولوية عالية):
- [ ] register.html
- [ ] dashboard.html
- [ ] join.html
- [ ] sections-manage.html
- [ ] sections-setup.html
- [ ] sections-dashboard.html
- [ ] create-project.html
- [ ] submit-project.html
- [ ] settings.html (تحديث - موجود بالفعل)

#### صفحات ثانوية:
- [ ] quick-login.html
- [ ] offline.html
- [ ] testing-index.html

---

## 🧪 الاختبار

### 1. افتح الصفحة في المتصفح
### 2. يجب أن ترى زر 🌙/☀️
### 3. اضغط الزر - يجب أن يتحول إلى Dark Mode
### 4. أعد تحميل الصفحة - يجب أن يبقى Dark Mode
### 5. افتح علامة تبويب أخرى - يجب أن تتزامن

---

## 🔧 API Reference

### Methods:

```javascript
// التحكم في الوضع
darkModeManager.enable();          // تفعيل Dark Mode
darkModeManager.disable();         // تعطيل Dark Mode
darkModeManager.toggle();          // تبديل الوضع
darkModeManager.isEnabled();       // التحقق من الحالة (true/false)
darkModeManager.reset();           // إعادة تعيين لتفضيل النظام

// إنشاء زر
darkModeManager.createToggle(
    container,  // HTMLElement أو null للـ body
    {
        position: 'top-right',
        size: 'medium',
        showLabel: false,
        customClass: ''
    }
);

// localStorage key
const isDark = localStorage.getItem('smartedu_darkMode') === 'true';
```

### Events:

```javascript
// الاستماع لتغييرات Dark Mode
window.addEventListener('darkmodechange', (e) => {
    console.log('Dark Mode:', e.detail.isDark);
});

// الاستماع لتغييرات localStorage من tabs أخرى
window.addEventListener('storage', (e) => {
    if (e.key === 'smartedu_darkMode') {
        console.log('Dark Mode changed in another tab');
    }
});
```

---

## 🎯 المزايا

✅ **localStorage Sync** - يحفظ التفضيل تلقائياً
✅ **Multi-tab Sync** - يتزامن بين علامات التبويب
✅ **System Preference** - يستخدم تفضيل النظام افتراضياً
✅ **Responsive** - يعمل على جميع الأجهزة
✅ **Customizable** - قابل للتخصيص بالكامل
✅ **Lightweight** - خفيف (<5KB)
✅ **No Dependencies** - لا يحتاج مكتبات خارجية
✅ **RTL Support** - يدعم اللغة العربية
✅ **Haptic Feedback** - ردود فعل لمسية على الجوال

---

## 🐛 Troubleshooting

### المشكلة: الزر لا يظهر
**الحل:**
1. تأكد من تحميل `dark-mode-manager.js` قبل استخدامه
2. تحقق من console للأخطاء
3. تأكد من وجود `darkModeManager` في window scope

### المشكلة: الألوان لا تتغير
**الحل:**
1. تأكد من وجود `dark-mode.css`
2. تحقق من متغيرات CSS
3. استخدم `var(--variable-name)` في CSS

### المشكلة: لا يحفظ التفضيل
**الحل:**
1. تحقق من localStorage في DevTools
2. تأكد من عدم وجود errors في console
3. تحقق من Storage permissions

---

## 📈 الخطوات التالية

1. ✅ إنشاء النظام
2. ✅ تطبيق على login.html
3. 📝 تطبيق على باقي الصفحات
4. 📝 اختبار شامل
5. 📝 تحسين الأداء
6. 📝 إضافة animations إضافية

---

## 💡 نصائح

1. **استخدم dark-mode-init.js** للتطبيق السريع
2. **أضف data-page-type** لتخصيص الموضع
3. **استمع لـ darkmodechange event** للتحديثات الديناميكية
4. **استخدم CSS variables** لسهولة التخصيص
5. **اختبر على أجهزة حقيقية** للتأكد من الـ performance

---

**تم بواسطة:** Cascade AI  
**التاريخ:** أكتوبر 2025
