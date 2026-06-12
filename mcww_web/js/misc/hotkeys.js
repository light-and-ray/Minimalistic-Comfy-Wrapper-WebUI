

function trySelectTab(tabNumber) {
    const tabsContainers = document.querySelectorAll('.mcww-page-tabs');
    tabsContainers.forEach((tabsContainer) => {
        if (!uiElementIsVisible(tabsContainer)) {
            return;
        }
        const tabs = tabsContainer.querySelectorAll('button[role="tab"], .overflow-dropdown button');
        if (tabNumber >= 1 && tabNumber <= tabs.length) {
            tabs[tabNumber - 1].click();
        }
    });
}

function activeElementEditable() {
    return document.activeElement.matches('textarea, input[type="text"], input[type="number"], ' +
                                                'input:not([type]), div.cm-content')
}

function tryModifySlider(difference, selector) {
    const sliders = document.querySelectorAll(selector);
    sliders.forEach((slider) => {
        if (!uiElementIsVisible(slider)) return;
        const currentValue = parseFloat(slider.value);
        const minValue = parseFloat(slider.min);
        const maxValue = parseFloat(slider.max);
        let newValue = currentValue + difference;
        if (newValue < minValue) newValue = minValue;
        if (newValue > maxValue) newValue = maxValue;
        slider.value = newValue;
        const event = new Event('input', {
            bubbles: true,
            cancelable: true,
        });
        slider.dispatchEvent(event);
    });
}


document.addEventListener('keydown', (event) => {
    const isCtrl = event.ctrlKey || event.metaKey;
    const lastMouseEvent = getLastMouseEvent();

    if (event.altKey && event.code === "KeyV") {
        new McwwClipboardHistoryMenu(lastMouseEvent);
        event.preventDefault();
    }
    if (event.code === "Escape") {
        event.stopPropagation(); // block gradio's behavior when its select the first element in gallery on escape
    }

    if (isCtrl && event.code === "KeyL") {
        const focusElements = document.querySelectorAll(".mcww-loras-filter textarea, .presets-filter textarea");
        for (const focusElement of focusElements) {
            if (!uiElementIsVisible(focusElement)) continue;
            event.preventDefault();
            focusElement.focus();
            focusElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            focusElement.select();
            break;
        }
    }

    if (isCtrl && !event.shiftKey && event.code === "KeyS") {
        event.preventDefault();
        clickVisibleButtons(".mcww-save-button");
    }
    if (isCtrl && event.shiftKey && event.code === "KeyS") {
        event.preventDefault();
        clickVisibleButtons(".mcww-shift-save-button");
    }


    if (activeElementEditable()) {
        if (event.code === "Escape") {
            document.activeElement.blur();
        }
        return;
    }


    const opacityDiff = 0.03;
    if (event.code === "Equal" || event.code == "NumpadAdd") {
        tryModifySlider(+opacityDiff, '.opacity-slider input[type="range"]');
    }
    if (event.code === "Minus" || event.code == "NumpadSubtract") {
        tryModifySlider(-opacityDiff, '.opacity-slider input[type="range"]');
    }
    if (event.code === "KeyS" && !event.shiftKey && !isCtrl) {
        clickVisibleButtons('button.mcww-swap, .mcww-swap input');
    }
    if (event.code === "KeyF" && (event.shiftKey || event.altKey)) {
        event.preventDefault();
        document.querySelector(".mcww-ui-fullscreen-button")?.click();
    }


    const inFullscreen = document.querySelector(".block.fullscreen");

    if (!inFullscreen) {
        if (isCtrl && event.code === "Enter") {
            clickVisibleButtons('.mcww-run-button');
            event.preventDefault();
        }
        if (event.code === "Escape") {
            closeSidebarOnMobile();
            clickVisibleButtons(".click-on-escape, button.toast-close, div.api-docs>div.backdrop");
        }
        if (event.code === "KeyR") {
            clickVisibleButtons(".mcww-refresh");
        }
        if (event.code === "KeyA") {
            clickVisibleButtons('.mcww-auto-refresh-checkbox input');
        }
        if (event.code === "KeyQ") {
            openPageOrGoBack("queue");
        }
        if (event.code === "KeyP") {
            ensureProjectIsSelected();
        }
        if (event.code === "KeyH") {
            openPageOrGoBack("helpers");
        }
        if (event.code === "KeyO") {
            openPageOrGoBack("options");
        }
        if (event.altKey || isCtrl) {
            if (event.code === "ArrowUp") {
                clickVisibleButtons(".mcww-queue-move-up");
            }
            if (event.code === "ArrowDown") {
                clickVisibleButtons(".mcww-queue-move-down");
            }
        } else {
            if (event.code === "ArrowUp") {
                trySelectPreviousQueueEntry();
            }
            if (event.code === "ArrowDown") {
                trySelectNextQueueEntry();
            }
        }
        if (
            (event.code >= "Digit1" && event.code <= "Digit9") ||
            (event.code >= "Numpad1" && event.code <= "Numpad9")
        ) {
            const enteredNumber = parseInt(event.code.replace(/Digit|Numpad/g, ""));
            trySelectTab(enteredNumber);
            trySelectTool(enteredNumber);
            trySelectQueuePriority(enteredNumber);
        }
        const brushSizeDiff = 0.5;
        if (event.code === "BracketRight" || event.code == "NumpadAdd") {
            tryModifySlider(+brushSizeDiff, '#brushSizeInput input[type="range"]');
        }
        if (event.code === "BracketLeft") {
            tryModifySlider(-brushSizeDiff, '#brushSizeInput input[type="range"]');
        }
        if (event.code === "KeyZ" && isCtrl) {
            if (event.shiftKey) {
                clickVisibleButtons("button.mcww-redo");
            } else {
                clickVisibleButtons("button.mcww-undo");
            }
        }
        if (event.code === "KeyY" && isCtrl) {
            clickVisibleButtons("button.mcww-redo");
        }
        if (event.code === "KeyC") {
            clickVisibleButtons("#colorPicker");
            if (getSelectedMainUIPage() === "compare") {
                goBack();
            }
        }
        if (event.code === "Backquote") {
            document.querySelector('.sidebar .toggle-button')?.click();
        }
    }
    else { // inFullscreen
        if (event.code === "KeyQ") {
            globalExitFullscreenIfExists();
        }
        if (event.code === "Escape") {
            globalExitFullscreenIfExists();
        }
    }

    if (event.code === "KeyW" && isCtrl && event.shiftKey && event.altKey && isInsidePWA()) {
        openPageOrGoBack("wolf3d"); // in not PWA user can change page directly in address bar
    }

    const galleryContainer = getGalleryContainerUnderCursor();

    if (galleryContainer) {
        if (event.code === "KeyS") {
            galleryContainer.querySelector('button[title="Download"], .download-text')?.click();
        }

        if (event.code === "KeyF") {
            if (!(isUIInFullscreen() && (event.shiftKey || event.altKey))) {
                // Don't open gallery fullscreen when user's intention is to close ui fullscreen
                galleryContainer.querySelector('button[title="Fullscreen"]')?.click();
            }
            galleryContainer.querySelector('button[title="Exit fullscreen mode"]')?.click();
        }

        if (event.code === "KeyA") {
            galleryContainer.querySelector('button.to-a')?.click();
        }

        if (event.code === "KeyB") {
            galleryContainer.querySelector('button.to-b')?.click();
        }

        if (event.code === "KeyC") {
            if (isCtrl) {
                galleryContainer.querySelector('button.copy')?.click();
            } else {
                galleryContainer.querySelector('button.compare')?.click();
            }
        }

        if (!event.altKey && isCtrl && event.code === "KeyV") {
            const pasteButton = querySelectorVisible(galleryContainer, 'button.paste');
            pasteButton?.click();
        }

        if (event.code === "Space") {
            const video = galleryContainer.querySelector('video');
            if (video && document.activeElement !== video) {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
                event.preventDefault();
            }
            const audioPlayPauseButton = galleryContainer.querySelector(".play-pause-button");
            if (audioPlayPauseButton) {
                audioPlayPauseButton.click();
                event.preventDefault();
            }
        }

        if (event.code === "KeyE") {
            const forceOpen = isCtrl || event.shiftKey;
            tryOpenEditorFromHotkey(galleryContainer, forceOpen);
        }

        if (event.code === "KeyM") {
            galleryContainer.querySelector(".markdown-toggle input")?.click();
        }

    } else { // not over a gallery
        if (!event.altKey && isCtrl && event.code === "KeyV") {
            querySelectorVisible(document, ".metadata-tab button.paste")?.click();
        }
    }

}, true);


window.addEventListener('paste', (event) => {
    const galleryContainer = getGalleryContainerUnderCursor();
    const metadataPasteButton = querySelectorVisible(document, ".metadata-tab button.paste");
    if (!galleryContainer?.querySelector("button.paste") && !metadataPasteButton) {
        openFileFromPasteEvent(event);
    }
});
