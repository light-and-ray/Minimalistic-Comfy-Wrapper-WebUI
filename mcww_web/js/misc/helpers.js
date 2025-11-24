
function scrollToComfyLogsBottom() {
    const logsElement = document.querySelector(".comfy-logs-code");
    if (!logsElement) return;
    logsElement.scrollTo({
        top: logsElement.scrollHeight,
        behavior: 'smooth'
    });
}


var needHideHelpersInfo = false;

function updateHelpersInfo() {
    const updateInfoButton = document.querySelector('button.mcww-update-helpers-info-button')
    if (updateInfoButton && uiElementIsVisible(updateInfoButton.parentElement)) {
        const overflowMenu = document.querySelector('.overflow-dropdown');
        if (!overflowMenu || !uiElementIsVisible(overflowMenu)) {
            updateInfoButton.click();
            needHideHelpersInfo = true;
        }
    } else {
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
                    showButton.click()
                    needHideHelpersInfo = false;
                }
            }
        }
    }
    setTimeout(updateHelpersInfo, 1000);
}

updateHelpersInfo();
