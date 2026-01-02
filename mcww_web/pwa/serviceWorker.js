const CACHE_NAME = 'mcww-pwa';
const ASSET_EXTENSIONS = ['.js', '.css'];
const CONNECT_TIMEOUT = 1000;
const CHECK_URL = '/config';

const shouldCache = (url) => {
    if (url === '/') return true;
    return ASSET_EXTENSIONS.some(ext => url.endsWith(ext));
};

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    if (shouldCache(url.pathname)) {
        event.respondWith(
            fetch(CHECK_URL, {
                method: 'HEAD',
                signal: AbortSignal.timeout(CONNECT_TIMEOUT)
            })
            .then(async () => {
                const networkResponse = await fetch(request);
                const cache = await caches.open(CACHE_NAME);
                cache.put(request, networkResponse.clone());
                return networkResponse;
            })
            .catch(() => {
                return caches.match(request);
            })
        );
    }
});