
function activateLoadingPlaceholder() {
    const activeWorkflowUIs = document.querySelectorAll(".workflow-ui");
    activeWorkflowUIs.forEach((activeWorkflowUI) => {
        if (!uiElementIsVisible(activeWorkflowUI)) {
            return;
        }
        const workflowUIParent = activeWorkflowUI.closest('.workflow-ui-parent');
        const workflowLoadingPlaceholder = workflowUIParent?.querySelector(".workflow-loading-placeholder");
        if (workflowLoadingPlaceholder) {
            activeWorkflowUI.classList.add("mcww-hidden");
            workflowLoadingPlaceholder.classList.remove("mcww-hidden");
        }
    });
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
    if (!updatedElements.querySelector(".project-media-prompt-tabs")) {
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


function clickInterruptButton() {
    document.querySelector(".mcww-interrupt-button")?.click();
}
