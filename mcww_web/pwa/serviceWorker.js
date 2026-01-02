const CACHE_NAME = 'mcww-pwa';
const ASSET_EXTENSIONS = ['.js', '.css'];
const TIMEOUT = 5000;

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
            // Try the network first
            fetch(request, { signal: AbortSignal.timeout(TIMEOUT) })
                .then(async (networkResponse) => {
                    // If network is successful, update the cache and return
                    const cache = await caches.open(CACHE_NAME);
                    cache.put(request, networkResponse.clone());
                    console.log(url.pathname, 'cached');
                    return networkResponse;
                })
                .catch(() => {
                    // If network fails (offline), look for it in the cache
                    console.log(url.pathname, 'from cache');
                    return caches.match(request);
                })
        );
    }
});