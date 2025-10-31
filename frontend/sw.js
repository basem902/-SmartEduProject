/**
 * Service Worker للـ PWA
 */

const CACHE_NAME = 'smartedu-v1.3.4';
const urlsToCache = [
  '/',
  '/index.html',
  '/pages/login.html',
  '/pages/register.html',
  '/pages/dashboard.html',
  '/pages/sections-setup.html',
  '/pages/join.html',
  '/pages/offline.html',
  '/assets/css/base.css',
  '/assets/css/dark-mode.css',
  '/assets/css/dashboard.css',
  '/assets/css/animations.css',
  '/assets/css/sections.css',
  '/assets/css/join.css',
  '/assets/js/config.js',
  '/assets/js/app.js',
  '/assets/js/api.js',
  '/assets/js/auth.js',
  '/assets/js/ui.js',
  '/assets/js/theme.js',
  '/assets/js/sections-api.js'
];

// تثبيت Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  self.skipWaiting(); // تفعيل فوري
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching files');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.error('Service Worker: Cache failed', err))
  );
});

// تفعيل Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache');
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim(); // السيطرة على جميع الصفحات
    })
  );
});

// اعتراض الطلبات
self.addEventListener('fetch', event => {
  const url = event.request.url;

  // تجاهل أي طلب ليس http/https (مثل chrome-extension)
  if (!url.startsWith('http')) {
    return; // دع المتصفح يتولى الطلب
  }

  // السماح لطلبات API بالمرور مباشرة للشبكة مع error handling
  if (url.includes('/api/') || url.includes('localhost:8000') || url.includes('onrender.com')) {
    event.respondWith(
      fetch(event.request)
        .catch(error => {
          // Log error silently without throwing in console
          console.info('SW: Network request failed (expected for CORS/offline):', event.request.url);
          // Return a basic error response instead of throwing
          return new Response(
            JSON.stringify({ error: 'Network request failed', offline: true }), 
            { 
              status: 503,
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
    );
    return;
  }

  // تجاهل غير GET
  if (event.request.method !== 'GET') {
    event.respondWith(fetch(event.request));
    return;
  }

  // تجاهل الطلبات عبر أصل مختلف
  const reqOrigin = new URL(url).origin;
  if (reqOrigin !== self.location.origin) {
    event.respondWith(fetch(event.request));
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) return response;

        return fetch(event.request)
          .then(response => {
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();

            caches.open(CACHE_NAME).then(cache => {
              try {
                cache.put(event.request, responseToCache);
              } catch (e) {
                // تجاهل أخطاء التخزين في الكاش
                console.warn('SW cache.put failed:', e && e.message);
              }
            });

            return response;
          })
          .catch(() => caches.match('/pages/offline.html'));
      })
  );
});

// استقبال الرسائل من التطبيق
self.addEventListener('message', event => {
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});
