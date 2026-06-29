

onUiUpdate((updatedElements) => {
    updatedElements.querySelectorAll(".cm-content").forEach(elem => elem.setAttribute('spellcheck', 'true'));
});


function showOfflinePlaceholder() {
    g_blockPageChange = true;
    const uiPages = document.querySelectorAll(".mcww-page-ui");
    uiPages.forEach((uiPage) => {
        uiPage.classList.remove("mcww-page-visible");
    });
    const placeholderElements = document.querySelectorAll('.offline-placeholder');
    placeholderElements.forEach((placeholderElement) => {
        placeholderElement.classList.remove('mcww-hidden');
        placeholderElement.classList.add('mcww-page-visible');
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
    document.addEventListener(eventName, (event) => {
        event.preventDefault();
    }, false);
});


onUiLoaded(() => {
    function checkForIsInsidePWA() {
        if (isInsidePWA()) {
            document.body.classList.add("pwa");
        } else {
            document.body.classList.remove("pwa");
        }
        TITLE.refresh();
    }
    checkForIsInsidePWA();
    if (window.isSecureContext) {
        document.body.classList.add("secure-context");
    }
    window.matchMedia('(display-mode: browser)').addEventListener('change', checkForIsInsidePWA);
});

const GRADIO_APP_BROKEN_MESSAGES = [
    "Connection to the server was lost. Attempting reconnection...",
    "Server stopped unexpectedly.",
    "This application is currently busy. Please try again.",
    "Connection re-established.",
];

const BLACKLISTED_TOASTED_MESSAGES = [
    "Waiting for file(s) to finish uploading, please retry.",
    "On mobile, the connection can break if this tab is unfocused or the device sleeps, losing your position in queue.",
    "Video not playable",
    "Reconnected to server, but the server has changed. You may need to refresh the page.",
] + GRADIO_APP_BROKEN_MESSAGES;

onUiUpdate((updatedElements) => {
    const toastMessages = updatedElements.querySelectorAll(".toast-body");
    toastMessages.forEach((toastMessage) => {
        const text = toastMessage.querySelector(".toast-text").textContent;
        if (BLACKLISTED_TOASTED_MESSAGES.includes(text)) {
            toastMessage.remove();
        }
        if (GRADIO_APP_BROKEN_MESSAGES.includes(text)) {
            onGradioAppBrokenMessageReceived();
        }
    });
});


function registerPageTabs(page) {
    onUiUpdate((updatedElements) => {
        const tabs = updatedElements.querySelectorAll('.mcww-page-tabs>div.tab-wrapper button[role="tab"]:not(.title-applied), ' +
                                        '.mcww-page-tabs>div.tab-wrapper .overflow-dropdown button:not(.title-applied)');
        for (const tab of tabs) {
            const pageElement = tab.closest(".mcww-page-ui");
            if (!pageElement.classList.contains(page)) continue;
            tab.onclick = () => {
                setSessionStorageVariable(`${page}LastTab`, tab.textContent);
                TITLE.setTab(page, tab.textContent);
            }
            if (tab.classList.contains("selected")) {
                TITLE.setTab(page, tab.textContent);
            }
            tab.classList.add("title-applied");
        }
    });
    onUiLoaded(() => {
        const lastTab = getSessionStorageVariable(`${page}LastTab`);
        if (!lastTab) return;
        const tabsSelector = `.mcww-page-ui.${page} ` + '.mcww-page-tabs>div.tab-wrapper button[role="tab"], ' +
                            `.mcww-page-ui.${page} ` + '.mcww-page-tabs>div.tab-wrapper .overflow-dropdown button';
        waitForElement(document, tabsSelector, () => {
            const tabs = document.querySelectorAll(tabsSelector);
            for (const tab of tabs) {
                if (tab.textContent === lastTab) {
                    tab.click();
                    return;
                }
            }
        });
    });
}
registerPageTabs("helpers");
registerPageTabs("options");


onUiLoaded(() => {
    OPTIONS.themeFlags.forEach((mcwwThemeFlag) => {
        document.body.classList.add(`mcww-theme-flag-${mcwwThemeFlag.toLowerCase().replace(" ", "-")}`);
    });
});


function bridgeTouchToMouse(element) {
    const map = {
        touchstart: "mousedown",
        touchmove: "mousemove",
        touchend: "mouseup"
    };

    function handler(event) {
        if (event.touches.length > 1) return;
        const touch = event.changedTouches[0];
        const type = map[event.type];
        const mouseEvent = new MouseEvent(type, {
            bubbles: true,
            cancelable: true,
            view: window,
            clientX: touch.clientX,
            clientY: touch.clientY,
            screenX: touch.screenX,
            screenY: touch.screenY,
            button: 0,
            buttons: 1
        });

        event.target.dispatchEvent(mouseEvent);

        if (event.cancelable) {
            event.preventDefault();
        }
    }

    addEventListenerWithCleanup(element, "touchstart", handler, { passive: false });
    addEventListenerWithCleanup(element, "touchmove", handler, { passive: false });
    addEventListenerWithCleanup(element, "touchend", handler, { passive: false });
}


onUiUpdate((updatedElements) => {
    const timeline = updatedElements.querySelector(".video-container #timeline:not(.patched)");
    if (timeline) {
        bridgeTouchToMouse(timeline);
        timeline.classList.add("patched");
    }
});


onUiLoaded(() => {
    const touchFullscreenGoBackButton = document.createElement("button");
    touchFullscreenGoBackButton.id = "touchFullscreenGoBackButton";
    touchFullscreenGoBackButton.onclick = goBack;
    touchFullscreenGoBackButton.textContent = "🡠 Go back";
    document.body.appendChild(touchFullscreenGoBackButton);
});


onUiUpdate((updatedElements) => {
    const items = updatedElements.querySelectorAll(".only-remove-dropdown .token:not(.patched-remove-on-click)");
    items.forEach((item) => {
        item.classList.add("patched-remove-on-click");
        item.onclick = (event) => {
            const removeButton = item.querySelector(".token-remove");
            if (event.target !== removeButton) {
                removeButton.click();
            }
        };
    });
});

