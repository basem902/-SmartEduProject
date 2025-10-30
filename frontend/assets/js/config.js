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

console.log('✅ Config loaded:', {
    environment: window.location.hostname === 'localhost' ? 'Development' : 'Production',
    API_BASE: API_BASE
});
