// Name of the cache
const CACHE_NAME = 'field-worker-cache-v1';

// List of files to cache
const urlsToCache = [
  '/',
  '/index.html', // Your HTML file
  '/sw.js',      // This service worker file
  'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css', // External Leaflet CSS
  'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js',  // External Leaflet JS
  'https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}' // Google Earth Hybrid tiles
];

// Install the service worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event handler: Serve cached content when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response from cache
        if (response) {
          return response;
        }

        // Clone the request if not in cache
        const fetchRequest = event.request.clone();
        return fetch(fetchRequest).then(response => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          // Open the cache and store the response
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });

          return response;
        });
      })
  );
});

// Activate the service worker and remove old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
