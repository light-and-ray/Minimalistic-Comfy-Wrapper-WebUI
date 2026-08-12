
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
        if (g_isTabActive && !isTabsOverflowMenuOpen()) {
            const checkboxes = document.querySelectorAll(".mcww-auto-refresh-checkbox input");
            for (const checkbox of checkboxes) {
                if (checkbox && checkbox.checked && uiElementIsVisible(checkbox)) {
                    clickVisibleButtons(".mcww-refresh");
                    break;
                }
            }
        }
    } finally {
        setTimeout(autoRefresh, 1000);
    }
}

autoRefresh();


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


async function on360VideoChange() {
    const video = document.querySelector("#video360 video");
    if (!video) {
        return 0.0;
    }
    if (video.readyState >= 1 && !isNaN(video.duration)) {
        return video.duration;
    }
    return new Promise((resolve) => {
        video.addEventListener("loadedmetadata", () => {
            resolve(video.duration);
        }, { once: true });
    });
}


onUiUpdate((updatedElements) => {
    updatedElements.querySelectorAll('#video360Slider:not(.attachedChange)').forEach((slider) => {
        slider.classList.add('attachedChange');

        let isDragging = false;

        const updateVideoFromAngle = (e) => {
            const rect = slider.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            const deltaX = e.clientX - centerX;
            const deltaY = e.clientY - centerY;

            // Calculate angle in radians starting from 12 o'clock (top)
            let angle = Math.atan2(deltaY, deltaX) + Math.PI / 2;
            if (angle < 0) {
                angle += 2 * Math.PI;
            }

            // Convert angle to a progress ratio between 0.0 and 1.0
            const progress = angle / (2 * Math.PI);

            // Recalculate video current time using duration
            const video = document.querySelector("#video360 video");
            if (video && !isNaN(video.duration) && video.duration > 0) {
                if (document.querySelector("#video360Inverted input")?.checked) {
                    video.currentTime = (1.0-progress) * video.duration;
                } else {
                    video.currentTime = progress * video.duration;
                }
            }

            // Optional: Store CSS custom variables for visual ring fill updates
            slider.style.setProperty('--progress', `${progress * 100}%`);
            slider.style.setProperty('--angle', `${angle * (180 / Math.PI)}deg`);
        };

        slider.addEventListener('pointerdown', (e) => {
            isDragging = true;
            const video360 = document.querySelector("#video360");
            video360.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            slider.setPointerCapture(e.pointerId);
            updateVideoFromAngle(e);
        });

        slider.addEventListener('pointermove', (e) => {
            if (isDragging) {
                updateVideoFromAngle(e);
            }
        });

        slider.addEventListener('pointerup', (e) => {
            if (isDragging) {
                isDragging = false;
                slider.releasePointerCapture(e.pointerId);
            }
        });

        slider.addEventListener('pointercancel', (e) => {
            if (isDragging) {
                isDragging = false;
                slider.releasePointerCapture(e.pointerId);
            }
        });
    });
});
