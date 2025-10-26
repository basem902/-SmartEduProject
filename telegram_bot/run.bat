@echo off
echo 🤖 Starting Telegram OTP Bot...
echo.

REM التحقق من وجود .env
if not exist .env (
    echo ❌ Error: .env file not found!
    echo 📝 Please create .env file from .env.example
    echo.
    echo    copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM التحقق من تثبيت المكتبات
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📦 Installing dependencies...
pip install -q -r requirements.txt

echo ✅ Setup complete!
echo.
echo 🚀 Starting bot...
echo.

python bot.py

pause
