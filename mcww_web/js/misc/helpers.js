
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


function applyMetadataDragOver() {
    const elements = document.querySelectorAll(".mcww-metadata-file:not(.patched), .mcww-metadata-uploaded:not(.patched)");
    if (elements.length > 0) {
        elements.forEach((element) => {
            element.classList.add("patched");
            element.addEventListener("dragover", (e) => {
                e.preventDefault();
                const clearButton = document.querySelector(".mcww-metadata-file button[title='Clear']");
                if (clearButton) {
                    clearButton.click();
                }
            });
        });
    }
}

onUiUpdate(applyMetadataDragOver);

