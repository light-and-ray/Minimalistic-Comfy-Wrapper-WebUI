
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


onUiUpdate(() => {
    const tabs = document.querySelectorAll('.show-tab-in-title>div.tab-wrapper button[role="tab"]:not(.title-applied), ' +
                                    '.show-tab-in-title>div.tab-wrapper .overflow-dropdown button:not(.title-applied)');
    for (const tab of tabs) {
        tab.onclick = () => {
            TITLE.setTab(tab.textContent);
        }
        if (tab.classList.contains("selected")) {
            TITLE.setTab(tab.textContent);
        }
        tab.classList.add("title-applied");
    }
});


function downloadCompareComposite() {
    const baseImage = document.querySelector(".compare-image-slider img:not(.fixed)");
    const topImage = document.querySelector(".compare-image-slider img.fixed");
    if (!baseImage || !topImage) {
        console.error('Could not find base or top image elements');
        return;
    }
    if (!baseImage.complete || !topImage.complete) {
        console.error('One or both images are not fully loaded.');
        return;
    }
    const topImageStyle = window.getComputedStyle(topImage);
    const opacity = parseFloat(topImageStyle.opacity) || 1.0;
    const compositeWidth = Math.max(baseImage.naturalWidth, topImage.naturalWidth);
    const compositeHeight = Math.max(baseImage.naturalHeight, topImage.naturalHeight);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = compositeWidth;
    canvas.height = compositeHeight;
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, compositeWidth, compositeHeight);
    const getDrawParams = (img, areaW, areaH) => {
        const imgRatio = img.naturalWidth / img.naturalHeight;
        const areaRatio = areaW / areaH;
        let w = areaW;
        let h = areaH;
        let x = 0;
        let y = 0;
        if (imgRatio > areaRatio) {
            h = areaW / imgRatio;
            y = (areaH - h) / 2; // Center vertically
        } else if (imgRatio < areaRatio) {
            w = areaH * imgRatio;
            x = (areaW - w) / 2; // Center horizontally
        }
        return { x, y, w, h };
    };
    const baseParams = getDrawParams(baseImage, compositeWidth, compositeHeight);
    ctx.drawImage(
        baseImage,
        baseParams.x,
        baseParams.y,
        baseParams.w,
        baseParams.h
    );
    const topParams = getDrawParams(topImage, compositeWidth, compositeHeight);
    ctx.globalAlpha = opacity;
    ctx.drawImage(
        topImage,
        topParams.x,
        topParams.y,
        topParams.w,
        topParams.h
    );
    ctx.globalAlpha = 1.0;
    const dataURL = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataURL;
    a.download = 'composite-image.png'; // Set the download file name
    document.body.appendChild(a); // Append to body is sometimes required for click() to work
    a.click();
    document.body.removeChild(a); // Clean up the temporary element
}


