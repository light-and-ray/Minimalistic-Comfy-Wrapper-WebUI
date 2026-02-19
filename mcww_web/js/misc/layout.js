

onUiUpdate((updatedElements) => {
    updatedElements.querySelectorAll(".cm-content").forEach(elem => elem.setAttribute('spellcheck', 'true'));
});


function showOfflinePlaceholder() {
    blockPageChange = true;
    const uiPages = document.querySelectorAll(".mcww-page-ui");
    uiPages.forEach((uiPage) => {
        uiPage.classList.remove("mcww-visible");
    });
    const placeholderElements = document.querySelectorAll('.offline-placeholder');
    placeholderElements.forEach((placeholderElement) => {
        placeholderElement.classList.remove('mcww-hidden');
        placeholderElement.classList.add('mcww-visible');
    });
    TITLE.setPage("Offline");
    TITLE.blockTitleChange = true;
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
    function checkForIsInsidePWA() {
        if (isInsidePWA()) {
            document.body.classList.add("pwa");
        } else {
            document.body.classList.remove("pwa");
        }
    }
    checkForIsInsidePWA();
    if (window.isSecureContext) {
        document.body.classList.add("secure-context");
    }
    window.matchMedia('(display-mode: standalone)').addEventListener('change', checkForIsInsidePWA);
});


const BLACKLISTED_TOASTED_MESSAGES = [
    "Waiting for file(s) to finish uploading, please retry.",
    "Video not playable",
];

onUiUpdate((updatedElements) => {
    const toastMessages = updatedElements.querySelectorAll(".toast-body");
    toastMessages.forEach((toastMessage) => {
        const text = toastMessage.querySelector(".toast-text").textContent;
        if (BLACKLISTED_TOASTED_MESSAGES.includes(text)) {
            toastMessage.style.display = "none";
        }
    });
});
