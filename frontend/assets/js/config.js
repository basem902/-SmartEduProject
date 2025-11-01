/**
 * Global Configuration
 * يُحمّل مرة واحدة فقط في جميع الصفحات
 */

// API Base URL - Smart Environment Detection
if (typeof window.API_BASE === 'undefined') {
    // Auto-detect environment
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        // Development
        window.API_BASE = 'http://localhost:8000/api';
    } else {
        // Production
        window.API_BASE = '/api';
    }
}

// Make it available as const for backward compatibility
const API_BASE = window.API_BASE;

// FastAPI Telegram Service URL (optional)
// إذا كنت تريد استخدام FastAPI منفصل، ضع URL هنا:
if (typeof window.FASTAPI_TELEGRAM_URL === 'undefined') {
    // للتفعيل: أزل التعليق وضع URL الخدمة
    // window.FASTAPI_TELEGRAM_URL = 'http://localhost:8001';
    // أو في Production:
    // window.FASTAPI_TELEGRAM_URL = 'https://smartedu-telegram.onrender.com';
    
    // افتراضياً: استخدم Django
    window.FASTAPI_TELEGRAM_URL = null;
}

console.log('✅ Config loaded:', {
    environment: window.location.hostname === 'localhost' ? 'Development' : 'Production',
    API_BASE: API_BASE,
    FASTAPI_TELEGRAM: window.FASTAPI_TELEGRAM_URL || 'Django (default)'
});
