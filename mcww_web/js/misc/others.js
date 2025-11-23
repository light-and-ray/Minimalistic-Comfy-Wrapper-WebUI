
function scrollToComfyLogsBottom() {
    const logsElement = document.querySelector(".comfy-logs-code");
    if (!logsElement) return;
    logsElement.scrollTo({
        top: logsElement.scrollHeight,
        behavior: 'smooth'
    });
}

onUiUpdate(() => {
    const tabButtons = document.querySelectorAll('.project-media-prompt-tabs .tab-container button[role="tab"]');
    const tabPanels = document.querySelectorAll('.project-media-prompt-tabs div[role="tabpanel"]');
    tabPanels.forEach((panel, index) => {
        const hasMedia = panel.querySelector('img, video') !== null;
        if (tabButtons[index]) {
            if (hasMedia) {
                tabButtons[index].classList.add('has-media');
            } else {
                tabButtons[index].classList.remove('has-media');
            }
        }
    });
});


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
