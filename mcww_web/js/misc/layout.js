

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
        waitForElement(tabsSelector, () => {
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
        document.body.classList.add(`mcww-theme-flag-${mcwwThemeFlag.toLowerCase()}`);
    });
});
