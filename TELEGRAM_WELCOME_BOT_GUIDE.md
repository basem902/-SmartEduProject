# 🤖 دليل Telegram Welcome Bot

## 📋 نظرة عامة

Bot يرحّب بالطلاب تلقائياً عند انضمامهم للقروبات ويحدّث Database

---

## ✅ المتطلبات

### 1. Python Packages

```bash
pip install python-telegram-bot requests django
```

أو من requirements.txt:
```bash
pip install -r backend/requirements.txt
```

### 2. Bot Token

✅ **موجود في .env**:
```env
TELEGRAM_BOT_TOKEN=8454359902:AAF-yYkwNnjbtg1O0juwxcOBXy4MlhnU4nU
TELEGRAM_BOT_USERNAME=SmartEduProjectsBot
```

---

## 🚀 طريقة التشغيل

### الخطوة 1: إضافة Bot للقروبات

1. افتح أي قروب تعليمي على Telegram
2. اذهب إلى **إعدادات القروب** → **Administrators**
3. اضغط **Add Admin** أو **Add Members**
4. ابحث عن: `@SmartEduProjectsBot`
5. أضفه كـ **Admin** مع صلاحيات:
   - ✅ **Add Members** (إضافة أعضاء)
   - ✅ **Send Messages** (إرسال رسائل)
   - ✅ **Delete Messages** (اختياري)

### الخطوة 2: تشغيل Bot

#### على Windows:
```powershell
cd C:\Users\basem\OneDrive\Desktop\Basem_test_windsurf\SmartEduProject
python telegram_welcome_bot.py
```

#### على Linux/Mac:
```bash
cd /path/to/SmartEduProject
python3 telegram_welcome_bot.py
```

### الخطوة 3: اختبار

1. افتح أي قروب يحتوي البوت
2. أضف عضو جديد (نفسك من حساب آخر مثلاً)
3. يجب أن ترى رسالة ترحيب من البوت فوراً! 🎉

---

## 📊 ماذا يفعل Bot؟

### 1️⃣ **يستقبل العضو الجديد**
```
🎉 مرحباً محمد أحمد علي حسن!
أهلاً بك في قروب ثانوي 3 - أ 📚
```

### 2️⃣ **يحدّث Database**
```python
✅ joined_telegram = True
✅ telegram_user_id = 123456789
✅ telegram_username = @student_username
✅ joined_at = 2025-11-02 00:05:00
```

### 3️⃣ **يعرض معلومات الشعبة**
```
📖 معلومات الشعبة:
🏫 المدرسة: ثانوية الإمام محمد بن سعود
📚 الصف: ثانوي - الصف 3 - المهارات الرقمية
📖 الشعبة: أ
```

---

## 🔍 كيف يتعرف Bot على الطالب؟

### السيناريو الأول (الأفضل):
```
1. الطالب يفتح join.html ويدخل اسمه
2. النظام يتحقق من الاسم في Database
3. يعرض رابط القروب
4. الطالب ينضم → Bot يعرف من هو (من student_id)
```

### السيناريو الثاني (تلقائي):
```
1. طالب جديد ينضم للقروب مباشرة
2. Bot يبحث عن أول طالب في هذه الشعبة لم ينضم بعد
3. يفترض أنه هو
4. يحدّث بياناته
```

### السيناريو الثالث (يدوي):
```
1. Bot لا يجد الطالب في Database
2. يرسل رسالة ترحيب عامة
3. المعلم يضيف الطالب يدوياً لاحقاً
```

---

## 🛠️ استكشاف الأخطاء

### ❌ المشكلة: Bot لا يرد

**الحلول**:
1. تأكد أن Bot مضاف كـ **Admin** في القروب
2. تأكد أن Bot يعمل (python telegram_welcome_bot.py)
3. افحص Logs في Terminal

### ❌ المشكلة: رسالة "القروب غير موجود في Database"

**الحل**:
```python
# تأكد أن القروب موجود في TelegramGroup Model
# يمكنك إضافته من sections-manage.html
```

### ❌ المشكلة: "لم نجد طالب مطابق"

**الحل**:
```python
# تأكد أن الطالب موجود في StudentRegistration
# يمكنك إضافته من add-students.html
```

---

## 📝 الـ Logs

### ما يجب أن تراه:
```
2025-11-02 00:05:00 - __main__ - INFO - 🤖 Bot بدأ العمل...
2025-11-02 00:05:00 - __main__ - INFO - 📡 API URL: http://localhost:8000/api
2025-11-02 00:05:00 - __main__ - INFO - 👂 في انتظار انضمام الطلاب...
2025-11-02 00:05:30 - __main__ - INFO - 👤 عضو جديد انضم: محمد (@student123, ID: 987654321)
2025-11-02 00:05:30 - __main__ - INFO - 📚 القروب: ثانوي 3 - أ - الشعبة: أ
2025-11-02 00:05:30 - __main__ - INFO - ✅ تم تحديث Database للطالب: محمد أحمد علي حسن
2025-11-02 00:05:30 - __main__ - INFO - ✅ تم إرسال رسالة الترحيب ل محمد أحمد علي حسن
```

---

## 🔧 التخصيص

### تعديل رسالة الترحيب:

افتح `telegram_welcome_bot.py` وابحث عن:
```python
welcome_message = f"""
🎉 **مرحباً {student_name}!**
...
"""
```

يمكنك تعديل:
- النص
- الأيموجي
- المعلومات المعروضة
- إضافة روابط
- إضافة صور (مع `send_photo`)

---

## 🚀 تشغيل مستمر (Production)

### على Windows (كخدمة):

استخدم **NSSM** (Non-Sucking Service Manager):
```powershell
# تحميل NSSM
# https://nssm.cc/download

# تثبيت كخدمة
nssm install TelegramBot python C:\Path\To\telegram_welcome_bot.py

# بدء الخدمة
nssm start TelegramBot
```

### على Linux (Systemd):

```bash
# إنشاء ملف الخدمة
sudo nano /etc/systemd/system/telegram-bot.service

# محتوى الملف:
[Unit]
Description=Telegram Welcome Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/SmartEduProject
ExecStart=/usr/bin/python3 telegram_welcome_bot.py
Restart=always

[Install]
WantedBy=multi-user.target

# تفعيل الخدمة
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# فحص الحالة
sudo systemctl status telegram-bot
```

### على Server (مع Docker):

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "telegram_welcome_bot.py"]
```

```bash
# بناء وتشغيل
docker build -t telegram-bot .
docker run -d --name telegram-bot telegram-bot
```

---

## 📊 مراقبة الأداء

### معلومات مفيدة:

```python
# في Database:
SELECT 
    COUNT(*) as total_students,
    COUNT(CASE WHEN joined_telegram = true THEN 1 END) as joined,
    ROUND(COUNT(CASE WHEN joined_telegram = true THEN 1 END) * 100.0 / COUNT(*), 2) as join_rate
FROM student_registrations;
```

### Dashboard سيعرض:
```
📊 إجمالي الطلاب: 50
✅ انضموا للتليجرام: 45
⏳ لم ينضموا بعد: 5
📈 نسبة الانضمام: 90%
```

---

## 🎯 الخطوات التالية

### ✅ تم:
1. ✅ تعديل join.html (التحقق من الطالب)
2. ✅ إنشاء API endpoint (تحديث Database)
3. ✅ إنشاء Telegram Bot (الترحيب)

### 🚀 للاختبار:
1. شغّل Backend: `python manage.py runserver`
2. شغّل Bot: `python telegram_welcome_bot.py`
3. افتح join.html وجرّب!

### 💡 تحسينات مستقبلية:
- إضافة أزرار تفاعلية (Inline Keyboards)
- إرسال المشاريع تلقائياً للطلاب الجدد
- إحصائيات مفصّلة لكل قروب
- إشعارات للمعلم عند انضمام طالب

---

## 📞 المساعدة

إذا واجهت مشكلة:
1. افحص Logs في Terminal
2. تأكد أن Bot مضاف كـ Admin
3. تأكد أن Backend يعمل
4. تحقق من .env (BOT_TOKEN + API_BASE_URL)

---

**آخر تحديث**: Nov 2, 2025  
**الحالة**: ✅ جاهز للاستخدام  
**Bot**: @SmartEduProjectsBot
