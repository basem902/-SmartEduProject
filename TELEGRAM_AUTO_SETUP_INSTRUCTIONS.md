# 📋 دليل إعداد نظام القروبات التلقائي

## ✅ ما تم إنجازه

### 1. Backend (مكتمل)
- ✅ إضافة حقول `telegram_id` و `telegram_username` لـ Teacher model
- ✅ إنشاء `telegram_groups.py` - Helper لإنشاء القروبات
- ✅ إنشاء API Endpoint: `POST /api/sections/telegram/create-groups/`
- ✅ إضافة URL في `sections/urls.py`

### 2. الملفات المُنشأة:
```
backend/apps/accounts/models.py          - معدّل ✅
backend/apps/sections/telegram_groups.py - جديد ✅
backend/apps/sections/views.py          - معدّل ✅
backend/apps/sections/urls.py           - معدّل ✅
backend/update_teacher_telegram.py      - script مساعد ✅
```

---

## 🔧 خطوات التفعيل

### الخطوة 1: تحديث قاعدة البيانات

```bash
cd backend

# إنشاء Migration
python manage.py makemigrations accounts

# تطبيق Migration
python manage.py migrate accounts

# أو تحديث مباشر بـ SQL
python manage.py dbshell
```

### الخطوة 2: تحديث معرف تيليجرام للمعلم

**Option A: عبر Django Shell**
```bash
python manage.py shell

from apps.accounts.models import Teacher
teacher = Teacher.objects.first()
teacher.telegram_id = 5844908352
teacher.save()
exit()
```

**Option B: عبر Script**
```bash
python update_teacher_telegram.py
```

**Option C: عبر SQL مباشرة**
```sql
UPDATE teachers SET telegram_id = 5844908352 WHERE id = 1;
```

### الخطوة 3: تثبيت مكتبة python-telegram-bot

```bash
cd backend
pip install python-telegram-bot==20.7
```

### الخطوة 4: التحقق من Bot Token

تأكد من وجود `TELEGRAM_BOT_TOKEN` في ملف `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

---

## 🎯 تعديلات Frontend المطلوبة

### ملف: `sections-setup.html`

#### التغيير 1: تبسيط الخطوة 4 (إزالة WhatsApp)

```html
<!-- Step 4: روابط القروبات -->
<div class="setup-form slide-in" id="step4" style="display: none;">
    <div class="form-section">
        <h3>🤖 إنشاء قروبات تيليجرام تلقائياً</h3>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">
            سيتم إنشاء قروب تيليجرام واحد لكل شعبة بضغطة واحدة
        </p>

        <!-- اسم المادة -->
        <div class="form-group">
            <label>📚 اسم المادة: <span style="color: red;">*</span></label>
            <input type="text" class="form-control" id="subjectName" 
                   placeholder="مثال: المهارات الرقمية" required>
            <small>سيظهر في اسم القروب</small>
        </div>

        <!-- زر الإنشاء التلقائي -->
        <div style="text-align: center; margin: 30px 0;">
            <button type="button" class="btn btn-success btn-lg" id="autoCreateGroups" 
                    style="padding: 15px 40px; font-size: 1.1rem;">
                <span id="autoCreateText">🤖 إنشاء القروبات تلقائياً</span>
                <span id="autoCreateSpinner" style="display: none;">
                    <span class="spinner-border spinner-border-sm"></span> جاري الإنشاء...
                </span>
            </button>
        </div>

        <!-- Progress Bar -->
        <div id="creationProgress" style="display: none; margin: 20px 0;">
            <div class="progress" style="height: 30px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" id="progressBar" style="width: 0%">
                    <span id="progressText">0/0</span>
                </div>
            </div>
        </div>

        <!-- نتائج الإنشاء -->
        <div id="creationResults" style="display: none; margin-top: 20px;">
            <h4>✅ تم إنشاء القروبات بنجاح!</h4>
            <div id="groupsList" class="groups-list">
                <!-- سيتم ملؤها ديناميكياً -->
            </div>
        </div>
    </div>

    <div class="form-actions">
        <button type="button" class="btn btn-secondary" id="prevStep4">← السابق</button>
        <button type="button" class="btn btn-primary" id="nextStep4" disabled>التالي →</button>
    </div>
</div>
```

#### التغيير 2: JavaScript Functions

```javascript
// في setupEventListeners()
document.getElementById('autoCreateGroups').addEventListener('click', autoCreateTelegramGroups);

// دالة إنشاء القروبات تلقائياً
async function autoCreateTelegramGroups() {
    const subjectName = document.getElementById('subjectName').value.trim();
    
    if (!subjectName) {
        UI.showToast('يجب إدخال اسم المادة', 'warning');
        return;
    }
    
    // تعطيل الزر وإظهار Spinner
    const btn = document.getElementById('autoCreateGroups');
    const text = document.getElementById('autoCreateText');
    const spinner = document.getElementById('autoCreateSpinner');
    
    btn.disabled = true;
    text.style.display = 'none';
    spinner.style.display = 'inline-block';
    
    // إظهار Progress Bar
    document.getElementById('creationProgress').style.display = 'block';
    
    try {
        // بناء قائمة الشُعب
        const sections = [];
        for (let i = 1; i <= setupState.sectionsCount; i++) {
            const arabicNumber = convertToArabicLetter(i);
            sections.push(arabicNumber);
        }
        
        // بناء اسم الصف
        const levelLabel = gradeConfig[setupState.level].label;
        const gradeName = `الصف ${getGradeText(setupState.gradeNumber)} ${levelLabel}`;
        
        // استدعاء API
        const response = await fetch(`${api.BASE_URL}/sections/telegram/create-groups/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${auth.getToken()}`
            },
            body: JSON.stringify({
                grade_name: gradeName,
                subject_name: subjectName,
                sections: sections
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || data.error || 'فشل إنشاء القروبات');
        }
        
        // معالجة النتائج
        handleGroupsCreation(data);
        
        // حفظ الروابط في setupState
        setupState.sectionLinks = data.groups.map((group, index) => ({
            section_number: index + 1,
            platform: 'telegram',
            whatsapp_link: '',
            telegram_link: group.invite_link || '',
            chat_id: group.chat_id
        }));
        
        // تفعيل زر التالي
        document.getElementById('nextStep4').disabled = false;
        
        UI.showToast('تم إنشاء القروبات بنجاح! 🎉', 'success');
        
    } catch (error) {
        console.error('Error creating groups:', error);
        UI.showToast(error.message, 'error');
        
        // إعادة تفعيل الزر
        btn.disabled = false;
        text.style.display = 'inline-block';
        spinner.style.display = 'none';
    }
}

// معالجة نتائج الإنشاء
function handleGroupsCreation(data) {
    const resultsDiv = document.getElementById('creationResults');
    const groupsList = document.getElementById('groupsList');
    
    let html = '<table class="table"><thead><tr>';
    html += '<th>الشعبة</th><th>الحالة</th><th>رابط القروب</th></tr></thead><tbody>';
    
    data.groups.forEach((group, index) => {
        const icon = group.success ? '✅' : '❌';
        const status = group.success ? 'تم الإنشاء' : 'فشل';
        const link = group.success 
            ? `<a href="${group.invite_link}" target="_blank">فتح القروب</a>` 
            : group.error;
        
        html += `<tr>
            <td><strong>شعبة ${convertToArabicLetter(index + 1)}</strong></td>
            <td>${icon} ${status}</td>
            <td>${link}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    
    // إظهار الإحصائيات
    html += `<div class="alert alert-info">
        <strong>الإحصائيات:</strong><br>
        ✅ نجح: ${data.statistics.success}<br>
        ❌ فشل: ${data.statistics.failed}<br>
        📊 الإجمالي: ${data.statistics.total}
    </div>`;
    
    groupsList.innerHTML = html;
    resultsDiv.style.display = 'block';
    
    // إخفاء زر الإنشاء
    document.getElementById('autoCreateGroups').style.display = 'none';
}

// تحويل الرقم إلى حرف عربي
function convertToArabicLetter(num) {
    const letters = ['أ', 'ب', 'ج', 'د', 'هـ', 'و', 'ز', 'ح', 'ط', 'ي', 
                     'ك', 'ل', 'م', 'ن', 'س', 'ع', 'ف', 'ص', 'ق', 'ر'];
    return letters[num - 1] || num.toString();
}

// الحصول على نص الصف
function getGradeText(num) {
    const arabicNumbers = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس', 'السادس'];
    return arabicNumbers[num - 1] || num.toString();
}
```

---

## 🧪 الاختبار

### 1. اختبار Backend API

```bash
# Test Endpoint
curl -X POST http://localhost:8000/api/sections/telegram/create-groups/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "grade_name": "الصف الثالث متوسط",
    "subject_name": "المهارات الرقمية",
    "sections": ["أ", "ب", "ج"]
  }'
```

### 2. اختبار Frontend

1. افتح `sections-setup.html`
2. أكمل الخطوات 1-3
3. في الخطوة 4:
   - أدخل اسم المادة
   - اضغط "إنشاء القروبات تلقائياً"
   - انتظر النتائج
4. تحقق من إنشاء القروبات في تيليجرام

---

## ⚠️ ملاحظات مهمة

### 1. صلاحيات البوت
تأكد أن البوت لديه صلاحية إنشاء قروبات في Telegram Bot API.

### 2. Rate Limiting
- Telegram يسمح بـ 20 قروب/دقيقة
- يوجد delay 3 ثواني بين كل قروب

### 3. معرف Telegram
- المعرف الخاص بك: `5844908352`
- يجب أن يكون محفوظ في قاعدة البيانات

### 4. نمط التسمية
- القالب: `"الصف الثالث أ - المهارات الرقمية"`
- يمكن تخصيصه من `telegram_groups.py`

---

## 📝 TODO List

- [ ] تطبيق Migration للـ telegram_id
- [ ] تحديث معرف تيليجرام للمعلم
- [ ] تثبيت python-telegram-bot
- [ ] تعديل sections-setup.html (Frontend)
- [ ] اختبار إنشاء قروب واحد
- [ ] اختبار إنشاء 5 قروبات
- [ ] التحقق من الأذونات في القروبات
- [ ] التحقق من الرسائل المثبتة

---

## 🆘 حل المشاكل الشائعة

### المشكلة: "TELEGRAM_BOT_TOKEN not found"
**الحل**: أضف التوكن في `.env`

### المشكلة: "معرف تيليجرام غير موجود"
**الحل**: نفّذ `update_teacher_telegram.py`

### المشكلة: "Bot doesn't have permission"
**الحل**: تحقق من صلاحيات البوت في BotFather

### المشكلة: "Rate limit exceeded"
**الحل**: انتظر دقيقة وحاول مرة أخرى

---

**آخر تحديث**: 19 أكتوبر 2025
**الحالة**: Backend جاهز ✅ | Frontend يحتاج تعديل ⚠️
