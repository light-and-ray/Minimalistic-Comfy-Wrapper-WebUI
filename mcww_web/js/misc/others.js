
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

