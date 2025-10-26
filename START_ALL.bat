@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════╗
echo ║          SmartEdu Project - تشغيل شامل                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM التحقق من الملفات
echo [1/6] التحقق من الملفات...
if not exist "backend\.env" (
    echo ❌ ملف backend\.env غير موجود
    echo.
    echo استخدم .env.FIXED كمرجع
    pause
    exit /b 1
)

if not exist "telegram_bot\.env.ready" (
    echo ℹ️  سننشئ telegram_bot\.env الآن...
    copy telegram_bot\.env.ready telegram_bot\.env >nul 2>&1
    if exist "telegram_bot\.env" (
        echo ✅ تم إنشاء telegram_bot\.env
    ) else (
        echo ⚠️  يرجى إنشاء telegram_bot\.env يدوياً
    )
)

echo ✅ الملفات موجودة
echo.

REM اختبار الإعدادات
echo [2/6] اختبار إعدادات Django...
python test_config.py
if errorlevel 1 (
    echo.
    echo ❌ خطأ في الإعدادات
    pause
    exit /b 1
)
echo.

REM تثبيت المكتبات
echo [3/6] التحقق من المكتبات...
cd backend
pip show django >nul 2>&1
if errorlevel 1 (
    echo تثبيت المكتبات...
    pip install -r requirements.txt
)
cd ..

cd telegram_bot
pip show python-telegram-bot >nul 2>&1
if errorlevel 1 (
    echo تثبيت مكتبات البوت...
    pip install -r requirements.txt
)
cd ..
echo ✅ المكتبات جاهزة
echo.

REM تشغيل Migrations
echo [4/6] إعداد قاعدة البيانات...
cd backend
python manage.py makemigrations otp_system
python manage.py migrate
cd ..
echo ✅ قاعدة البيانات جاهزة
echo.

echo [5/6] إنشاء superuser (إذا لم يكن موجوداً)...
cd backend
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='basem902').exists() or User.objects.create_superuser('basem902', 'basem902@gmail.com', 'Zxcvb123asd@')" 2>nul
cd ..
echo ✅ Superuser جاهز (basem902 / Zxcvb123asd@)
echo.

echo [6/6] تشغيل الخوادم...
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  سيتم فتح 3 نوافذ:                                       ║
echo ║  1️⃣  Django Backend (port 8000)                           ║
echo ║  2️⃣  Telegram Bot                                         ║
echo ║  3️⃣  Frontend (افتح يدوياً: Live Server)                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause

REM تشغيل Django
start "Django Backend" cmd /k "cd backend && python manage.py runserver"

REM انتظار 3 ثواني
timeout /t 3 /nobreak >nul

REM تشغيل البوت
start "Telegram Bot" cmd /k "cd telegram_bot && python bot.py"

echo.
echo ✅ تم تشغيل الخوادم!
echo.
echo 📋 الروابط:
echo   Backend:  http://localhost:8000
echo   Admin:    http://localhost:8000/admin
echo   Frontend: http://localhost:5500 (Live Server)
echo.
echo 🤖 Telegram Bot: @SmartEduProjectBot
echo.
echo 📊 للمراقبة:
echo   Django Logs:  في نافذة Django Backend
echo   Bot Logs:     في نافذة Telegram Bot
echo.
pause
