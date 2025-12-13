
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

onUiUpdate(() => {
    document.querySelectorAll(".cm-content").forEach(elem => elem.setAttribute('spellcheck', 'true'));
});


function onRunButtonCopyClick() {
    document.querySelector('.mcww-run-button')?.click();
}
