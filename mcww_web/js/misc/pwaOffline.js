
function showOfflinePlaceholder() {
    // removeStartupLoader();
    const placeholderElements = document.querySelectorAll('.offline-placeholder');
    placeholderElements.forEach((placeholderElement) => {
        placeholderElement.classList.remove('mcww-hidden');
        placeholderElement.classList.add('mcww-visible');
    });
}

const setupOfflineHandler = () => {
    const serviceWorkerUrl = '/pwa/serviceWorker.js';

    navigator.serviceWorker.register(serviceWorkerUrl, { scope: '/' })
        .catch(err => {
            console.error('SW registration failed:', err);
        });
};

onUiLoaded(setupOfflineHandler);

