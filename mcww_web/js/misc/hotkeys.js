
function clickVisibleButton(selector) {
    const buttons = document.querySelectorAll(selector);
    for (const button of buttons) {
        if (uiElementIsVisible(button)) {
            button?.click();
        }
    }
}

function trySelectTab(tabNumber) {
    const tabs = document.querySelectorAll('.tabs-with-hotkeys button[role="tab"], .tabs-with-hotkeys .overflow-dropdown button');
    if (tabNumber >= 1 && tabNumber <= tabs.length) {
        tabs[tabNumber - 1].click();
    }
}


document.addEventListener('keydown', (event) => {
    const isCtrl = event.ctrlKey || event.metaKey;
    if (isCtrl && event.code === "Enter") {
        document.querySelector('.mcww-run-button')?.click();
        event.preventDefault();
    }
    if (isCtrl && !event.shiftKey && event.code === "KeyS") {
        event.preventDefault();
        clickVisibleButton(".mcww-save-button");
    }
    if (event.code === "Escape") {
        globalExitFullscreenIfExists();
        closeSidebarOnMobile();
        clickVisibleButton(".click-on-escape, button.toast-close, div.api-docs>div.backdrop");
    }

    if (document.activeElement.matches('textarea, input[type="text"], div.cm-content')) {
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
            tryMoveQueueEntryUp();
        }
        if (event.code === "ArrowDown") {
            tryMoveQueueEntryDown();
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
        container = elementUnderCursor.closest('.gallery-container, .image-container, .video-container, .mcww-other-galley');
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

