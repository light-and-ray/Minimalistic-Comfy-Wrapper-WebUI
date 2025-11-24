
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
                const overflowMenu = document.querySelector('.overflow-dropdown');
                if (!overflowMenu || !uiElementIsVisible(overflowMenu)) {
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
