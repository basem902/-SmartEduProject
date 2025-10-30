// API config shim for submit-project page
(function(){
  try {
    // Ensure base from global config if present
    var hostname = window.location.hostname;
    if (typeof window.API_BASE === 'undefined' || !window.API_BASE) {
      if (hostname === 'localhost' || hostname === '127.0.0.1') {
        window.API_BASE = 'http://localhost:8000/api';
      } else {
        // Use Netlify proxy in production
        window.API_BASE = '/api';
      }
    }
    // Backward-compat var expected by submit-project.js
    window.API_BASE_URL = window.API_BASE;
    console.log('🧩 api-config loaded', { API_BASE: window.API_BASE, API_BASE_URL: window.API_BASE_URL });
  } catch (e) {
    console.error('api-config init error', e);
  }
})();
