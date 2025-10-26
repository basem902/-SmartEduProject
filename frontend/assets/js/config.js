/**
 * Global Configuration
 * يُحمّل مرة واحدة فقط في جميع الصفحات
 */

// API Base URL - Global Variable
if (typeof window.API_BASE === 'undefined') {
    window.API_BASE = 'http://localhost:8000/api';
}

// Make it available as const for backward compatibility
const API_BASE = window.API_BASE;

console.log('✅ Config loaded: API_BASE =', API_BASE);
