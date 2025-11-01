@echo off
echo Starting Telegram FastAPI Service...
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Copy .env if not exists
if not exist ".env" (
    if exist ".env.example" (
        echo Copying .env.example to .env...
        copy .env.example .env
        echo Please edit .env with your credentials!
        pause
    )
)

REM Run FastAPI
echo.
echo Starting FastAPI on http://localhost:8001
echo.
python main.py
