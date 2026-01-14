

onUiUpdate(() => {
    document.querySelectorAll(".cm-content").forEach(elem => elem.setAttribute('spellcheck', 'true'));
});


function applyPreventPullToRefresh() {
    if (!OPTIONS.preventPullToRefreshGesture) return;
    let startY = 0;
    let isPullingDown = false;

    document.addEventListener('touchstart', function(e) {
        if (window.scrollY !== 0) return;
        const touch = e.touches[0];
        const element = document.elementFromPoint(touch.clientX, touch.clientY);
        if (isScrollableTop(element)) {
            isPullingDown = false;
            return;
        }
        if (element.matches('input[type="range"]')) return;
        startY = touch.clientY;
        isPullingDown = true;
    }, { passive: false });

    document.addEventListener('touchmove', function(e) {
        if (!isPullingDown || window.scrollY !== 0 || e.touches.length > 1) return;
        const currentY = e.touches[0].clientY;
        const diff = currentY - startY;
        if (diff > 0) {
            e.preventDefault();
        }
    }, { passive: false });

    document.addEventListener('touchend', function() {
        if (isPullingDown) {
            isPullingDown = false;
        }
    }, { passive: false });
}

onUiLoaded(applyPreventPullToRefresh);


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


const setupPwaServiceWorker = () => {
    const serviceWorkerUrl = '/pwa/serviceWorker.js';
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register(serviceWorkerUrl, { scope: '/' })
            .catch(error => {
                console.error('service worker registration failed:', error);
            });
    }
};

onUiLoaded(setupPwaServiceWorker);


['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    document.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
    }, false);
});


document.addEventListener('contextmenu', (e) => {
    if (!isInsidePWA()) {
        return;
    }
    if (e.target.matches('a, textarea, input[type="text"], div.cm-content, img, video, audio')) {
        return;
    }
    const selection = window.getSelection();
    const selectedText = selection.toString();
    if (selectedText.length > 0) {
        return;
    }
    if (e.shiftKey) {
        return;
    }
    e.preventDefault();
});
