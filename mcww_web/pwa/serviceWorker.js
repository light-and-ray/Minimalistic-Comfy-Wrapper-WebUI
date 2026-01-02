const CACHE_NAME = 'mcww-pwa';
const ASSET_EXTENSIONS = ['.js', '.css'];
const CONNECT_TIMEOUT = 6000;
const FETCH_TIMEOUT = 15000;
const CHECK_OFFLINE_INTERVAL = 3000;
const CHECK_URL = '/config';
let isOffline = false;

async function _checkOffline() {
    let isTimeout = false;
    try {
        await fetch(CHECK_URL, { method: 'HEAD', signal: AbortSignal.timeout(CONNECT_TIMEOUT) });
        isOffline = false;
    } catch (error) {
        if (error.name === 'TimeoutError') {
            isTimeout = true;
        }
        isOffline = true;
    } finally {
        setTimeout(_checkOffline, isTimeout ? 0 : CHECK_OFFLINE_INTERVAL);
    }
}
_checkOffline();

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
        event.respondWith((async () => {
            async function getCachedResponse() {
                return await caches.match(request, {
                    ignoreSearch: url.pathname === '/'
                });
            }

            // Path A: Offline - return cache immediately
            if (isOffline) {
                const cached = await getCachedResponse();
                if (cached) return cached;
            }

            // Path B: Standard request
            try {
                const networkResponse = await fetch(request, { signal: AbortSignal.timeout(FETCH_TIMEOUT) });
                const cache = await caches.open(CACHE_NAME);
                cache.put(request, networkResponse.clone());
                return networkResponse;
            } catch (error) {
                // Path C: Offline/Timeout - Fallback to cache
                const cached = await getCachedResponse();
                if (cached) return cached;
                throw error;
            }
        })());
    }
});


// Optimized listener for CHECK_URL
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // If the app tries to fetch the CHECK_URL, we serve the SW's internal state
    if (url.pathname === CHECK_URL) {
        event.respondWith((async () => {
            if (isOffline) {
                return new Response(JSON.stringify(null), {
                    status: 503,
                    headers: { 'Content-Type': 'application/json' }
                })
            } else {
                return await fetch(request, { signal: AbortSignal.timeout(FETCH_TIMEOUT) })
            }

        })());
    }
});
