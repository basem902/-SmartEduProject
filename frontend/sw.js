/**
 * Service Worker للـ PWA
 */

const CACHE_NAME = 'smartedu-v1.2.0';
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
  // السماح لطلبات API بالمرور مباشرة للشبكة
  if (event.request.url.includes('/api/') || event.request.url.includes('localhost:8000')) {
    event.respondWith(fetch(event.request));
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // إرجاع من Cache إذا وُجد
        if (response) {
          return response;
        }

        // محاولة جلب من الشبكة
        return fetch(event.request)
          .then(response => {
            // التحقق من صحة الاستجابة
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // نسخ الاستجابة
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // إرجاع صفحة offline عند انقطاع الاتصال
            return caches.match('/pages/offline.html');
          });
      })
  );
});

// استقبال الرسائل من التطبيق
self.addEventListener('message', event => {
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});
