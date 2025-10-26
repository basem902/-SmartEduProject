#!/bin/bash

echo "🤖 Starting Telegram OTP Bot..."
echo ""

# التحقق من وجود .env
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please create .env file from .env.example"
    echo ""
    echo "   cp .env.example .env"
    echo ""
    exit 1
fi

# التحقق من تثبيت المكتبات
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🚀 Starting bot..."
echo ""

python bot.py
