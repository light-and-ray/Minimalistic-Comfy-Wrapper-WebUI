

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
    window.matchMedia('(display-mode: standalone)').addEventListener('change', checkForIsInsidePWA);
});

const GRADIO_APP_BROKEN_MESSAGE = "Connection to the server was lost. Attempting reconnection...";
const BLACKLISTED_TOASTED_MESSAGES = [
    "Waiting for file(s) to finish uploading, please retry.",
    "Ожидание завершения загрузки файла(ов), пожалуйста, повторите попытку.",
    "Laukiama, kol bus baigti įkelti failai, prašome bandyti dar kartą.",
    "ファイルのアップロードが完了するのを待っています。再度お試しください",
    "等待文件上传完成，请稍后重试。",
    "等待檔案上傳完成，請稍後重試。",
    "Чекаємо завершення завантаження файлу(ів), будь ласка, спробуйте ще раз.",
    "Aguardando o(s) arquivo(s) terminar(em) de ser carregado(s), por favor, tente novamente.",
    "Oczekiwanie na zakończenie przesyłania pliku(ów), proszę spróbować ponownie.",
    "Wachten tot het uploaden van bestand(en) is voltooid, probeer het opnieuw.",
    "파일 업로드가 완료될 때까지 기다렸다가 다시 시도해주세요.",
    "En attente de la fin du téléchargement des fichier(s), veuillez réessayer.",
    "Odotetaan tiedostojen lataamisen päättymistä, yritä uudelleen.",
    "Warten auf das Hochladen der Datei(en), bitte versuchen Sie es erneut.",
    "Väntar på att fil(er) ska vara klara att ladda upp, vänligen försök igen.",
    "Fayl(lar) yuklanib bo'lishini kutish, iltimos, qayta urinib ko'ring.",
    "கோப்பு(கள்) பதிவேற்றம் முடிவடைய காத்திருக்கிறது, தயவுசெய்து மீண்டும் முயற்சிக்கவும்.",
    "Esperando a que se complete(n) la(s) carga(s) de archivo(s), por favor inténtelo de nuevo.",
    "إنتظر انتهاء رفع الملف(ات)، يرجى إعادة المحاولة.",
    "फाइलें अपलोड होने का इंतजार कर रहे हैं, कृपया पुन: प्रयास करें।",
    "מחכים לסיום העלאה של הקבצים, אנא נסה שוב.",
    "در انتظار به پایان رسیدن بارگذاری فایل‌ها، لطفاً مجدداً امتحان کنید.",

    "Video not playable",
    GRADIO_APP_BROKEN_MESSAGE,
    "Connection re-established.",
];

onUiUpdate((updatedElements) => {
    const toastMessages = updatedElements.querySelectorAll(".toast-body");
    toastMessages.forEach((toastMessage) => {
        const text = toastMessage.querySelector(".toast-text").textContent;
        if (BLACKLISTED_TOASTED_MESSAGES.includes(text)) {
            toastMessage.style.display = "none";
        }
        if (text === GRADIO_APP_BROKEN_MESSAGE) {
            onGradioAppBroken();
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
        document.body.classList.add(`mcww-theme-flag-${mcwwThemeFlag.toLowerCase()}`);
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

