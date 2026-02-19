
function clickVisibleButton(selector) {
    const buttons = document.querySelectorAll(selector);
    for (const button of buttons) {
        if (uiElementIsVisible(button)) {
            button?.click();
        }
    }
}

function trySelectTab(tabNumber) {
    const tabsContainers = document.querySelectorAll('.tabs-with-hotkeys');
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
    if (isCtrl && event.code === "Enter") {
        clickVisibleButton('.mcww-run-button');
        event.preventDefault();
    }
    if (isCtrl && !event.shiftKey && event.code === "KeyS") {
        event.preventDefault();
        clickVisibleButton(".mcww-save-button");
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
    if (event.code === "Escape") {
        globalExitFullscreenIfExists();
        closeSidebarOnMobile();
        clickVisibleButton(".click-on-escape, button.toast-close, div.api-docs>div.backdrop");
    }

    if (document.activeElement.matches('textarea, input[type="text"], input:not([type]), div.cm-content')) {
        if (event.code === "Escape") {
            document.activeElement.blur();
        }
        return;
    }

    if (event.code === "KeyR") {
        clickVisibleButton(".mcww-refresh");
    }
    if (event.code === "KeyA") {
        clickVisibleButton('.mcww-auto-refresh-checkbox input');
    }
    if (event.code === "KeyQ") {
        document.querySelector(".mcww-queue")?.click();
    }
    if (event.code === "KeyH") {
        document.querySelector(".mcww-helpers-button")?.click();
    }
    if (event.code === "KeyP") {
        ensureProjectIsSelected();
    }
    if (event.code === "KeyO") {
        document.querySelector(".mcww-options-button")?.click();
    }
    if (event.altKey || isCtrl) {
        if (event.code === "ArrowUp") {
            clickVisibleButton(".mcww-queue-move-up");
        }
        if (event.code === "ArrowDown") {
            clickVisibleButton(".mcww-queue-move-down");
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
    }
    if (event.code === "KeyS" && !event.shiftKey && !isCtrl) {
        clickVisibleButton('button.mcww-swap, .mcww-swap input');
    }
    const opacityDiff = 0.03;
    if (event.code === "Equal" || event.code == "NumpadAdd") {
        tryModifySlider(+opacityDiff, '.opacity-slider input[type="range"]');
    }
    if (event.code === "Minus" || event.code == "NumpadSubtract") {
        tryModifySlider(-opacityDiff, '.opacity-slider input[type="range"]');
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
            clickVisibleButton("button.mcww-redo");
        } else {
            clickVisibleButton("button.mcww-undo");
        }
    }
    if (event.code === "KeyY" && isCtrl) {
        clickVisibleButton("button.mcww-redo");
    }
    if (event.code === "KeyC") {
        clickVisibleButton("#colorPicker");
    }
    if (event.code === "Backquote") {
        document.querySelector('.sidebar .toggle-button')?.click();
    }

    const lastMouseEvent = getLastMouseEvent();
    const elementUnderCursor = document.elementFromPoint(lastMouseEvent.clientX, lastMouseEvent.clientY);
    let container = null;
    if (elementUnderCursor) {
        container = elementUnderCursor.closest('.gallery-container, .image-container, .video-container, .mcww-other-gallery');
    }

    if (container) {
        if (event.code === "KeyS") {
            container.querySelector('button[title="Download"]')?.click();
        }

        if (event.code === "KeyF") {
            container.querySelector('button[title="Exit fullscreen mode"], button[title="Fullscreen"]')?.click();
        }

        if (event.code === "KeyA") {
            container.querySelector('button.to-a')?.click();
        }

        if (event.code === "KeyB") {
            container.querySelector('button.to-b')?.click();
        }

        if (event.code === "KeyC") {
            if (isCtrl) {
                container.querySelector('button.copy')?.click();
            } else {
                container.querySelector('button.compare')?.click();
            }
        }

        if (isCtrl && event.code === "KeyV") {
            container.querySelector('button.paste')?.click();
        }

        if (event.code === "Space") {
            const video = container.querySelector('video');
            if (video && document.activeElement !== video) {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
                event.preventDefault();
            }
            const audioPlayPauseButton = container.querySelector(".play-pause-button");
            if (audioPlayPauseButton) {
                audioPlayPauseButton.click();
                event.preventDefault();
            }
        }

        if (event.code === "KeyE") {
            const forceOpen = isCtrl || event.shiftKey;
            tryOpenEditorFromHotkey(container, forceOpen);
        }

    }

});

