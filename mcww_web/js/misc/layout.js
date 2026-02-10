

onUiUpdate((updatedElements) => {
    updatedElements.querySelectorAll(".cm-content").forEach(elem => elem.setAttribute('spellcheck', 'true'));
});


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
    TITLE.setPage("Offline");
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
    if (e.shiftKey) {
        return;
    }
    if (e.target.matches('a, img, video, audio, '
                        + 'textarea:not([disabled]), '
                        + 'input[type="text"]:not([disabled]), '
                        + 'div.cm-content[contenteditable="true"] *'
    )) {
        return;
    }
    const selection = window.getSelection();
    const selectedText = selection.toString();
    if (selectedText.length > 0) {
        return;
    }
    e.preventDefault();
});


onUiLoaded(() => {
    if (isInsidePWA()) {
        document.body.classList.add("pwa");
    }
});


const BLACKLISTED_TOASTED_MESSAGES = ["Waiting for file(s) to finish uploading, please retry."];

onUiUpdate((updatedElements) => {
    const toastMessages = updatedElements.querySelectorAll(".toast-body");
    toastMessages.forEach((toastMessage) => {
        const text = toastMessage.querySelector(".toast-text").textContent;
        if (BLACKLISTED_TOASTED_MESSAGES.includes(text)) {
            toastMessage.style.display = "none";
        }
    });
});
