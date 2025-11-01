#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Telethon and cryptg first (critical for Telegram features)
echo "📦 Installing Telethon and cryptg separately..."
pip install --no-cache-dir telethon>=1.34.0 cryptg>=0.4.0 || echo "⚠️ Warning: Telethon/cryptg installation failed"

# Install dependencies (use production requirements if exists)
if [ -f requirements-production.txt ]; then
    echo "📦 Installing production dependencies..."
    pip install --no-cache-dir -r requirements-production.txt
else
    echo "📦 Installing all dependencies..."
    pip install --no-cache-dir -r requirements.txt
fi

# Verify Telethon installation
echo "🔍 Verifying Telethon installation..."
python -c "import telethon; print(f'✅ Telethon version: {telethon.__version__}')" || echo "❌ Telethon not installed!"
python -c "import cryptg; print(f'✅ Cryptg installed')" || echo "❌ Cryptg not installed!"

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if doesn't exist (optional)
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@smartedu.com', 'Admin@12345')
    print('✅ Superuser created')
else:
    print('✅ Superuser already exists')
EOF
