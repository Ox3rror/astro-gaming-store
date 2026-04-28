const CACHE_NAME = 'astro-gaming-v1';
const STATIC_ASSETS = [
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/img/logo.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
];

// Install — cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate — clear old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch — cache-first for static, network-first for pages
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Static assets — cache first
  if (url.pathname.startsWith('/static/') ||
      request.url.includes('cdn.jsdelivr.net') ||
      request.url.includes('fonts.googleapis.com') ||
      request.url.includes('fonts.gstatic.com')) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(c => c.put(request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // HTML pages — network first, fallback to cache
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(c => c.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request).then(cached => {
          if (cached) return cached;
          // Offline fallback
          return new Response(`
            <!DOCTYPE html><html><head>
            <meta charset="UTF-8"/><title>Offline — Astro Gaming Store</title>
            <style>
              body{font-family:Inter,sans-serif;background:#0F1117;color:#fff;
                   display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
              .box{text-align:center;padding:40px;}
              img{width:120px;margin-bottom:24px;opacity:.8;}
              h2{color:#2563EB;margin-bottom:8px;}
              p{color:#8896A5;font-size:14px;}
              button{margin-top:20px;background:#2563EB;color:#fff;border:none;
                     padding:10px 24px;border-radius:8px;cursor:pointer;font-size:14px;}
            </style></head><body>
            <div class="box">
              <img src="/static/img/logo.png" alt="Astro Gaming Store"/>
              <h2>You're Offline</h2>
              <p>No internet connection detected.<br>
                 Previously visited pages may still be available.</p>
              <button onclick="location.reload()">Try Again</button>
            </div></body></html>
          `, { headers: { 'Content-Type': 'text/html' } });
        }))
    );
    return;
  }

  // Default — network with cache fallback
  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});
