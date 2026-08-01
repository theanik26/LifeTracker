const CACHE_NAME = 'lifetrack-v1';
const ASSETS = [
  '/',
  '/dashboard',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/dashboard.js',
  '/static/img/icon-192.jpg',
  '/static/img/icon-512.jpg'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      // Allow caching to fail gracefully on partial static assets
      return cache.addAll(ASSETS).catch(err => console.log("Cache pre-fill skipped: ", err));
    })
  );
});

self.addEventListener('fetch', event => {
  // Pass-through fetch handler (required by Chrome PWA installation checks)
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
