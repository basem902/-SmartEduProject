# 🔍 **تعليمات Debug المشكلة**

## ⚠️ **المشكلة المتكررة 5 مرات**

```
400 Bad Request:
{
  "section_ids": {"0": ["الرجاء إدخال رقم صحيح صالح."]},
  "allowed_file_types": {"0": ["Not a valid string."]},
  "external_links": {"0": ["الرجاء إدخال رابط إلكتروني صالح."]}
}
```

---

## 🔧 **خطوات Debug الإلزامية:**

### **1. أعد تشغيل Backend (CRITICAL!)** ⚡

```bash
# أوقف Backend (Ctrl+C)
# ثم شغّله من جديد:
cd c:\Users\basem\OneDrive\Desktop\Basem_test_windsurf\SmartEduProject\backend
python manage.py runserver
```

**⚠️ بدون restart، التغييرات لن تعمل!**

---

### **2. امسح Cache المتصفح:**

```
1. افتح DevTools (F12)
2. اضغط بيمين على زر Refresh
3. اختر "Empty Cache and Hard Reload"
```

---

### **3. جرّب إنشاء مشروع:**

1. ✅ افتح `create-project.html`
2. ✅ املأ جميع الحقول
3. ✅ اختر شُعب (مهم!)
4. ✅ اختر file types (مهم!)
5. ✅ اضغط "حفظ المشروع"

---

### **4. راقب Django Console:**

يجب أن ترى هذا:

```
================================================================================
🔍 RAW REQUEST DATA:
Content-Type: multipart/form-data
request.data type: <class 'rest_framework.utils.serializers_helpers.QueryDict'>

  section_ids:
    - get(): 1 (type: <class 'str'>)
    - getlist(): ['1', '2', '3']
    
  allowed_file_types:
    - get(): pdf (type: <class 'str'>)
    - getlist(): ['pdf', 'video']
    
  external_links:
    - get(): None (type: <class 'NoneType'>)
    - getlist(): []

================================================================================
✅ section_ids from getlist (native): ['1', '2', '3']
✅ allowed_file_types from getlist (native): ['pdf', 'video']
✅ external_links from getlist (native): []
================================================================================
📊 PARSED DATA BEFORE VALIDATION:
  section_ids: [1, 2, 3] (type: <class 'list'>, length: 3)
  allowed_file_types: ['pdf', 'video'] (type: <class 'list'>, length: 2)
  external_links: [] (type: <class 'list'>, length: 0)
  grade_id: 7 (type: <class 'int'>)
================================================================================
```

---

### **5. راقب Browser Console:**

يجب أن ترى:

```
📤 Submitting project data:
🔍 Sections before sending: [1, 2, 3]
🔍 File types before sending: ["pdf", "video"]
🔍 External links before sending: []
📋 FormData contents:
  section_ids: [1, 2, 3]
  allowed_file_types: [pdf, video]
  grade_id: 7
  title: مشروع الفيديو
  ...
```

---

## 🚨 **إذا استمرت المشكلة:**

### **افحص هذه الأمور:**

#### **1. هل تم restart Backend؟**
```bash
# يجب أن ترى:
Starting development server at http://127.0.0.1:8000/
```

#### **2. هل الـ sections موجودة في DB؟**
```bash
python manage.py shell
>>> from apps.sections.models import Section
>>> Section.objects.all()
# يجب أن ترى شُعب
```

#### **3. هل الـ grade_id صحيح؟**
```bash
>>> from apps.sections.models import Grade
>>> Grade.objects.all()
# يجب أن ترى صفوف
```

---

## 📝 **أرسل لي هذه المعلومات:**

### **من Django Console:**

```
1. نص الـ RAW REQUEST DATA كامل
2. نص الـ PARSED DATA BEFORE VALIDATION
3. نص الـ SERIALIZER VALIDATION FAILED (إن وُجد)
```

### **من Browser Console:**

```
1. نص الـ FormData contents كامل
2. أي أخطاء في console
```

### **من Network Tab:**

```
1. Request Headers
2. Request Payload
3. Response (status + body)
```

---

## 💡 **حلول محتملة إضافية:**

### **الحل 1: تأكد من وجود بيانات:**
```javascript
// في Browser Console:
console.log('projectData:', projectData);
console.log('sections:', projectData.sections);
console.log('allowedFileTypes:', projectData.settings.allowedFileTypes);
```

### **الحل 2: تأكد من الـ validation:**
```python
# في Django shell:
from apps.projects.serializers_new import ProjectCreateSerializer

data = {
    'section_ids': [1, 2, 3],
    'allowed_file_types': ['pdf', 'video'],
    'external_links': [],
    # ... باقي البيانات
}

serializer = ProjectCreateSerializer(data=data)
print(serializer.is_valid())
print(serializer.errors)
```

---

## 🎯 **المشكلة المحتملة:**

إذا كان logging يعرض:
```
allowed_file_types: ['pdf', 'video'] ← صحيح
section_ids: [1, 2, 3] ← صحيح
```

**ولكن** لا يزال هناك خطأ `{"0": ["..."]}`، فهذا يعني:

1. ❌ Backend لم يُعد تشغيله
2. ❌ أو Cache لم يُمسح
3. ❌ أو الملف القديم لا يزال يعمل

---

## ✅ **الحل النهائي:**

```bash
# 1. أوقف كل شيء
Ctrl+C في Backend

# 2. امسح __pycache__
cd backend
find . -type d -name __pycache__ -exec rm -rf {} +

# 3. شغّل من جديد
python manage.py runserver

# 4. امسح cache المتصفح
Ctrl+Shift+R

# 5. جرّب من جديد
```

---

**📞 بعد تطبيق هذه الخطوات، أرسل لي نتائج logging!**
