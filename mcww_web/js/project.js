
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


waitForElement(document, ".project-workflow-ui", () => {
    waitForElement(document, ".hide-init-workflow-loader", (button) => {
        button.click();
    });
}, null);


function onRunButtonCopyClick() {
    document.querySelector('.mcww-run-button')?.click();
}


onUiUpdate((updatedElements) => {
    const mediaTypes = ["project-mediaSingle", "project-mediaBatch", "queue-mediaBatch"];
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


onWorkflowRendered((workflowUIParent) => {
    const workflowName = workflowUIParent?.querySelector(".workflows-radio label.selected span");
    if (workflowName) {
        TITLE.setSelectedProjectWorkflow(workflowName.textContent);
    }
});


onPageSelected((page) => {
    if (page === "project") {
        calculatePresetDatasetHeights();
    }
})


function showRunButtonMouseAlert() {
    mouseAlert("Running...", 700);
}

onWorkflowRendered((workflowUIParent) => {
    const toBatch = workflowUIParent.querySelector('#toBatch');
    const tabBatch = workflowUIParent.querySelector('#tabBatch');

    while (toBatch?.firstChild) {
        tabBatch.appendChild(toBatch.firstChild);
    }
});


async function getWorkflowUIStorageKey(workflowUIParent) {
    const button = await waitForElementAsync(workflowUIParent, '.mcww-pull', 300);
    const pullData = JSON.parse(button.textContent || button.innerText);
    const storageKey = `workflow-ui-state-${pullData.outputs_key}`;
    return storageKey;
}


async function saveWorkflowUIState() {
    const workflowUIParent = document.querySelector(".mcww-page-ui.project.workflow-ui-parent");
    const storageKey = await getWorkflowUIStorageKey(workflowUIParent);
    const needSaveElements = workflowUIParent.querySelectorAll(".need-save-state");
    const stateArray = [];
    let index = 0;
    for (const needSaveElement of needSaveElements) {
        if (needSaveElement.classList.contains("tabs")) {
            const tabButtons = Array.from(needSaveElement.querySelectorAll(
                ':scope > div.tab-wrapper button[role="tab"], :scope > div.tab-wrapper .overflow-dropdown button'
            ));
            const selectedIndex = tabButtons.findIndex(x => x.matches(".selected, .overflow-item-selected"));
            stateArray.push({
                type: "tabs",
                elementIndex: index,
                selectedIndex: selectedIndex,
            });
        } else if (needSaveElement.classList.contains("accordion")) {
            const isOpen = needSaveElement.querySelector(":scope > button.open") !== null;
            stateArray.push({
                type: "accordion",
                elementIndex: index,
                open: isOpen,
            });
        } else if (needSaveElement.classList.contains("checkbox")) {
            const input = needSaveElement.querySelector('input[type="checkbox"]');
            stateArray.push({
                type: "checkbox",
                elementIndex: index,
                checked: input?.checked,
            });
        }
        index += 1;
    }

    setBrowserStorageVariable(storageKey, stateArray);
}


onWorkflowRendered(async (workflowUIParent) => {
    const storageKey = await getWorkflowUIStorageKey(workflowUIParent);
    const needLoadElements = workflowUIParent.querySelectorAll(".need-save-state");
    const stateArray = getBrowserStorageVariable(storageKey);
    if (!stateArray) return;
    let index = 0;
    stateArray.forEach((state) => {
        const needLoadElement = needLoadElements[state.elementIndex];
        if (needLoadElement) {
            if (state.type === "tabs") {
                const tabButtons = Array.from(needLoadElement.querySelectorAll(
                    ':scope > div.tab-wrapper button[role="tab"], :scope > div.tab-wrapper .overflow-dropdown button'
                ));
                tabButtons[state.selectedIndex]?.click();
            } else if (state.type == "accordion") {
                const isOpen = needLoadElement.querySelector(":scope > button.open") !== null;
                if (state.open != isOpen) {
                    needLoadElement.querySelector(":scope > button")?.click();
                }
            } else if (state.type == "checkbox") {
                const input = needLoadElement.querySelector('input[type="checkbox"]');
                if (state.checked != input.checked) {
                    input.click();
                }
            }
        }
    });
});

