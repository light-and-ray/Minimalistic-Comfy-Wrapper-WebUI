
function showOfflinePlaceholder() {
    const initUI = document.querySelector('.init-ui');
    if (initUI) {
        initUI.classList.add('mcww-hidden');
    }
    const placeholderElements = document.querySelectorAll('.offline-placeholder');
    placeholderElements.forEach((placeholderElement) => {
        placeholderElement.classList.remove('mcww-hidden');
        placeholderElement.classList.add('mcww-visible');
    });
    applyPreventPullToRefresh();
}

const setupOfflineHandler = () => {
    const serviceWorkerUrl = '/pwa/serviceWorker.js';
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register(serviceWorkerUrl, { scope: '/' })
            .catch(error => {
                console.error('service worker registration failed:', error);
            });
    }
};

onUiLoaded(setupOfflineHandler);

