"""
Django settings for SmartEduProject.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',  # ✅ WebSocket support
    
    # Local apps
    'apps.accounts',
    'apps.projects',
    'apps.admin_panel',
    'apps.sections',
    'apps.otp_system',
]

MIDDLEWARE = [
    'core.cors_middleware.CorsMiddleware',  # ✅ Custom CORS - MUST be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ For static files on Render
    'corsheaders.middleware.CorsMiddleware',  # Backup CORS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database (Supabase PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # ✅ WhiteNoise

# Media files (User uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',
        'user': '100/minute',
    }
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', 1440))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
cors_origins_str = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5500,http://127.0.0.1:5500')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]

# CORS Configuration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# CORS Headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# CSRF Settings for Production
CSRF_TRUSTED_ORIGINS = [
    'https://smartedu-basem.netlify.app',
    'https://smarteduproject-k0um.onrender.com',
    'https://*.onrender.com',
    'https://*.netlify.app',
]

# Debug CORS
print("=" * 80)
print("🔍 CORS CONFIGURATION:")
print(f"  - CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
print(f"  - CORS_ALLOW_ALL_ORIGINS: {CORS_ALLOW_ALL_ORIGINS}")
print(f"  - CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
print(f"  - CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
print(f"  - DEBUG: {DEBUG}")
print("=" * 80)

# Email Settings (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('SMTP_PORT', 465))
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv('SMTP_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('SMTP_EMAIL')

# File Upload Settings
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 104857600))  # 100MB
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,xlsx,jpg,jpeg,png,mp4,mp3,wav').split(',')

# ClamAV Settings
CLAMAV_HOST = os.getenv('CLAMAV_HOST', '127.0.0.1')
CLAMAV_PORT = int(os.getenv('CLAMAV_PORT', 3310))

# Frontend URL
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5500')

# Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "data:")

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', None)  # ⚠️ أضف Token في .env
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', 'SmartEduProjectBot')

# ✅ للاختبار فقط - احذف بعد إضافة Token في .env
if not TELEGRAM_BOT_TOKEN:
    import sys
    print("=" * 60, file=sys.stderr)
    print("⚠️ تحذير: TELEGRAM_BOT_TOKEN غير موجود!", file=sys.stderr)
    print("   → أضفه في .env لإرسال الإشعارات", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

# Telegram API Configuration
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')

OTP_SECRET_KEY = os.getenv('OTP_SECRET_KEY', SECRET_KEY)

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Frontend URL
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5500')

# ============================================================
# WebSocket & Channels Configuration
# ============================================================

ASGI_APPLICATION = 'core.asgi.application'

# Channel layers (in-memory for development, Redis for production)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
        # For production with Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [('127.0.0.1', 6379)],
        # },
    }
}

# ============================================================
# Celery Configuration (Background Tasks)
# ============================================================

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Riyadh'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# ============================================================
# AI Validation Settings
# ============================================================

AI_VALIDATION_ENABLED = os.getenv('AI_VALIDATION_ENABLED', 'True').lower() == 'true'
AI_DEFAULT_THRESHOLD = int(os.getenv('AI_DEFAULT_THRESHOLD', '70'))
PLAGIARISM_THRESHOLD = int(os.getenv('PLAGIARISM_THRESHOLD', '50'))
MAX_SUBMISSION_ATTEMPTS = int(os.getenv('MAX_SUBMISSION_ATTEMPTS', '5'))

# Video Processing
VIDEO_MAX_DURATION = int(os.getenv('VIDEO_MAX_DURATION', '30'))
VIDEO_MIN_DURATION = int(os.getenv('VIDEO_MIN_DURATION', '15'))
VIDEO_MAX_SIZE_MB = int(os.getenv('VIDEO_MAX_SIZE_MB', '50'))
VIDEO_ALLOWED_FORMATS = os.getenv('VIDEO_ALLOWED_FORMATS', 'mp4,mov,avi').split(',')

# OCR Settings
TESSERACT_LANGUAGES = os.getenv('TESSERACT_LANGUAGES', 'ara+eng')
