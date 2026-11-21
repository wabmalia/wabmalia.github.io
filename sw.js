// Service worker for the installed arcade app. Its scope is the whole site, so
// it also controls the games under /<repo>/. Games must not register their own
// service worker: one at /<repo>/ would take that path over from this one.
//
// For now it only steps in for page loads: they go to the network as usual, and
// when that fails (offline) the offline page is shown instead of the browser's
// error. Everything else (game assets, PeerJS, analytics) is left alone.
const CACHE = 'arcade-v1';
const OFFLINE = '/offline.html';

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll([OFFLINE])));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key !== CACHE) await caches.delete(key);
    // Start the page request while the worker boots, so pages don't wait on it.
    if (self.registration.navigationPreload) await self.registration.navigationPreload.enable();
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  if (event.request.mode !== 'navigate') return;
  event.respondWith((async () => {
    try {
      return (await event.preloadResponse) || (await fetch(event.request));
    } catch {
      return (await caches.match(OFFLINE)) || Response.error();
    }
  })());
});
