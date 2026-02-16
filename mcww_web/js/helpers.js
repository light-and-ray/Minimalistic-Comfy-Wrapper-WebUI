
function scrollToComfyLogsBottom() {
    const logsElement = document.querySelector(".comfy-logs-code");
    if (!logsElement) return;
    logsElement.scrollTo({
        top: logsElement.scrollHeight,
        behavior: 'smooth'
    });
}


let helpersInfoUpdateInProgress = false;

function helpersInfoUpdateIsDone() {
    helpersInfoUpdateInProgress = false;
}

async function waitForHelpersInfoUpdate() {
    const startTime = Date.now();
    while (helpersInfoUpdateInProgress && (Date.now() - startTime < 7000)) {
        await sleep(100);
    }
    if (helpersInfoUpdateInProgress) {
        console.warn(`[${new Date().toLocaleTimeString()}] Helpers info update operation timed out`);
        helpersInfoUpdateInProgress = false;
    }
}


var needHideHelpersInfo = false;

async function updateHelpersInfo() {
    try {
        const updateInfoButton = document.querySelector('button.mcww-update-helpers-info-button');
        if (updateInfoButton && uiElementIsVisible(updateInfoButton.parentElement)) {
            try {
                if (!isTabsOverflowMenuOpen()) {
                    updateInfoButton.click();
                    needHideHelpersInfo = true;
                    helpersInfoUpdateInProgress = true;
                    await waitForHelpersInfoUpdate();
                }
            } catch (error) {
                console.error("Error while handling overflow menu or update button:", error);
            }
        } else {
            try {
                const showButton = document.querySelector('button.mcww-show-helpers-info-button');
                const hideButton = document.querySelector('button.mcww-hide-helpers-info-button');
                const row = showButton?.parentElement;

                if (row) {
                    if (!uiElementIsVisible(row)) {
                        if (hideButton && needHideHelpersInfo) {
                            hideButton.click();
                            needHideHelpersInfo = false;
                        }
                    } else {
                        if (showButton) {
                            showButton.click();
                            needHideHelpersInfo = false;
                        }
                    }
                }
            } catch (error) {
                console.error("Error while handling show/hide buttons or row visibility:", error);
            }
        }
    } catch (error) {
        console.error("Unexpected error in updateHelpersInfo:", error);
    } finally {
        setTimeout(updateHelpersInfo, 1000);
    }
}

updateHelpersInfo();


function autoRefresh() {
    try {
        if (!isTabsOverflowMenuOpen()) {
            const checkboxes = document.querySelectorAll(".mcww-auto-refresh-checkbox input");
            for (const checkbox of checkboxes) {
                if (checkbox && checkbox.checked && uiElementIsVisible(checkbox)) {
                    clickVisibleButton(".mcww-refresh");
                    break;
                }
            }
        }
    } finally {
        setTimeout(autoRefresh, 1000);
    }
}

autoRefresh();


onUiLoaded(() => {
    const tabs = document.querySelectorAll('.show-tab-in-title>div.tab-wrapper button[role="tab"]:not(.title-applied), ' +
                                    '.show-tab-in-title>div.tab-wrapper .overflow-dropdown button:not(.title-applied)');
    for (const tab of tabs) {
        tab.onclick = () => {
            setSessionStorageVariable("helpersLastTab", tab.textContent);
            TITLE.setTab(tab.textContent);
        }
        if (tab.classList.contains("selected")) {
            TITLE.setTab(tab.textContent);
        }
        tab.classList.add("title-applied");
    }
});


onUiLoaded(() => {
    if (getSelectedMainUIPageFromUrl() === "helpers") {
        const lastTab = getSessionStorageVariable("helpersLastTab");
        if (!lastTab) return;
        const tabsSelector = '.show-tab-in-title>div.tab-wrapper button[role="tab"], ' +
                                    '.show-tab-in-title>div.tab-wrapper .overflow-dropdown button';
        waitForElement(tabsSelector, () => {
            const tabs = document.querySelectorAll(tabsSelector);
            for (const tab of tabs) {
                if (tab.textContent === lastTab) {
                    tab.click();
                    return;
                }
            }
        });
    }
});


let installPrompt = null;

window.addEventListener("beforeinstallprompt", (event) => {
    installPrompt = event;
});

function installAsPWA() {
    if (!installPrompt) {
        return false;
    }
    installPrompt.prompt();
    return true;
}


function applyCloseOnDragOverMetadataAutomatic(updatedElements) {
    const elements = updatedElements.querySelectorAll(".mcww-metadata-uploaded:not(.drag-over-metadata-patched)");
    if (elements.length > 0) {
        elements.forEach((element) => {
            element.classList.add("drag-over-metadata-patched");
            addEventListenerWithCleanup(element, "dragover", (e) => {
                const hasFiles = e.dataTransfer && Array.from(e.dataTransfer.types).includes('Files');
                if (!hasFiles) {
                    return;
                }
                e.preventDefault();
                const clearButton = document.querySelector(".mcww-metadata-file button[title='Clear']");
                if (clearButton) {
                    clearButton.click();
                }
            });
        });
    }
}

onUiUpdate(applyCloseOnDragOverMetadataAutomatic);
