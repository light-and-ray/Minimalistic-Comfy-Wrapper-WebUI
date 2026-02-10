
function activateLoadingPlaceholder() {
    let activeWorkflowUI = document.querySelector(".active-workflow-ui");
    let workflowLoadingPlaceholder = document.querySelector(".workflow-loading-placeholder");
    if (activeWorkflowUI && workflowLoadingPlaceholder) {
        activeWorkflowUI.classList.add("mcww-hidden");
        workflowLoadingPlaceholder.classList.remove("mcww-hidden");
    }
}


waitForElement(".project-workflow-ui", () => {
    waitForElement(".hide-init-workflow-loader", (button) => {
        button.click();
    });
}, null);


function onRunButtonCopyClick() {
    document.querySelector('.mcww-run-button')?.click();
}


onUiUpdate((updatedElements, removedElements) => {
    if (!updatedElements.querySelector("img, video") && !removedElements.querySelector("img, video")) {
        return
    };
    const mediaTypes = ["mediaSingle", "mediaBatch"];
    for (mediaType of mediaTypes) {
        const tabButtons = document.querySelectorAll(`.project-media-prompt-tabs.${mediaType} .tab-container button[role="tab"]`);
        const tabPanels = document.querySelectorAll(`.project-media-prompt-tabs.${mediaType} div[role="tabpanel"]`);
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
    }
});
