#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies (use production requirements if exists)
if [ -f requirements-production.txt ]; then
    echo "📦 Installing production dependencies..."
    pip install -r requirements-production.txt
else
    echo "📦 Installing all dependencies..."
    pip install -r requirements.txt
fi

# Verify Telethon installation
echo "🔍 Verifying Telethon installation..."
python -c "import telethon; print(f'✅ Telethon version: {telethon.__version__}')" || echo "❌ Telethon not installed!"

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
