@echo off
echo ============================================
echo   Telegram Bot Setup
echo ============================================
echo.

REM إنشاء ملف .env للبوت
if not exist telegram_bot\.env (
    echo Creating telegram_bot\.env...
    copy telegram_bot\env_template.txt telegram_bot\.env
    echo ✅ Created telegram_bot\.env
) else (
    echo ℹ️  telegram_bot\.env already exists
)

echo.
echo ============================================
echo   الخطوات التالية:
echo ============================================
echo.
echo 1. افتح backend\.env
echo    أضف في النهاية:
echo.
type TELEGRAM_CONFIG.txt | findstr /V "DATABASE_URL API_BASE_URL LOG_"
echo.
echo 2. تأكد من وجود telegram_bot\.env
echo.
echo 3. شغّل Django:
echo    cd backend
echo    python manage.py runserver
echo.
echo 4. شغّل البوت:
echo    cd telegram_bot
echo    python bot.py
echo.
echo ============================================
pause
