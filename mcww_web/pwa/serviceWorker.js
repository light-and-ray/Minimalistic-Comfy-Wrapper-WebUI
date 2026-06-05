const CACHE_NAME = 'mcww-pwa-cache-v7';
const CACHE_EXTENSIONS = ['.js', '.css', '.woff2'];
const CONNECT_TIMEOUT = 6000;
const FETCH_TIMEOUT = 15000;
const CHECK_OFFLINE_INTERVAL = 3000;
const CHECK_URL = '/config';
let isOffline = false;
let lastConfig = null;


async function _checkOffline() {
    let isTimeout = false;
    const controller = new AbortController();
    const connectTimer = setTimeout(() => {
        controller.abort(new Error('ConnectTimeout'));
    }, CONNECT_TIMEOUT);

    try {
        const response = await fetch(CHECK_URL, { signal: controller.signal });
        clearTimeout(connectTimer);
        isOffline = false;

        const fetchTimer = setTimeout(() => {
            controller.abort(new Error('FetchTimeout'));
        }, FETCH_TIMEOUT);

        response.blob()
            .then((blob) => {
                clearTimeout(fetchTimer);
                lastConfig = new Response(blob, {
                    status: response.status,
                    statusText: response.statusText,
                    headers: response.headers
                });
            })
            .catch((bodyError) => {
                clearTimeout(fetchTimer);
                console.warn('Body download failed or timed out:', bodyError.message);
            });

    } catch (error) {
        clearTimeout(connectTimer);
        if (error.name === 'AbortError' || error.message === 'ConnectTimeout') {
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
    return CACHE_EXTENSIONS.some(ext => url.endsWith(ext));
};


self.addEventListener('install', (event) => {
    self.skipWaiting();
});


self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                    return Promise.resolve();
                })
            );
        })
    );
});


self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    if (shouldCache(url.pathname)) {
        const options = {
            ignoreSearch: url.pathname === '/'
        };

        event.respondWith((async () => {
            async function getCachedResponse() {
                return await caches.match(request, options);
            }

            // Path A: Offline - return cache immediately
            if (isOffline) {
                const cached = await getCachedResponse();
                if (cached) return cached;
            }

            // Path B: Standard request
            try {
                const networkResponse = await fetch(request, { signal: AbortSignal.timeout(FETCH_TIMEOUT) });
                const responseClone = networkResponse.clone();
                caches.open(CACHE_NAME).then(async (cache) => {
                    await cache.delete(request, options);
                    await cache.put(request, responseClone);
                });
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


// Optimized listener for CHECK_URL (backend check function)
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    if (url.pathname === CHECK_URL) {
        event.respondWith((async () => {
            if (isOffline || lastConfig === null) {
                return new Response(JSON.stringify(null), {
                    status: 503,
                    headers: { 'Content-Type': 'application/json' }
                })
            } else {
                return lastConfig.clone();
            }
        })());
    }
});
