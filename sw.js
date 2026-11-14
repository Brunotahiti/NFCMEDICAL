/* MédiParc NFC : service worker. Rend le site installable (Android) et garde l'interface et les photos
   en cache pour un démarrage rapide. Les données (/materiel/api/) ne sont jamais mises en cache. */
const CACHE = 'mediparc-v1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(k => Promise.all(k.filter(x => x !== CACHE).map(x => caches.delete(x)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin || u.pathname.startsWith('/materiel/api/')) return;
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(x => x.put('/materiel/', c)); } return r; })
      .catch(() => caches.match('/materiel/')));
    return;
  }
  if (/^\/materiel\/(photos|icons)\//.test(u.pathname)) {
    e.respondWith(caches.match(e.request).then(m => m || fetch(e.request).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); } return r; })));
  }
});
