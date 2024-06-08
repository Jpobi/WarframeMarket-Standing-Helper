// static/service-worker.js
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open('pwa-cache-v1').then(function(cache) {
            return cache.addAll([
                '/',
                '/static/style.css',
                '/static/app.js',
                '/templates/index.html'
            ]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});
