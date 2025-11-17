
function clickVisibleButton(selector) {
    const buttons = document.querySelectorAll(selector);
    for (const button of buttons) {
        if (uiElementIsVisible(button)) {
            button?.click();
            return;
        }
    }
}

function trySelectTab(tabNumber) {
    const tabs = document.querySelectorAll('.tabs-with-hotkeys button[role="tab"]');
    if (tabNumber >= 1 && tabNumber <= tabs.length) {
        tabs[tabNumber - 1].click();
    }
}


document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.code === "Enter") {
        clickVisibleButton('.mcww-run-button');
        event.preventDefault();
    }
    if (event.ctrlKey && !event.shiftKey && event.code === "KeyS") {
        event.preventDefault();
        clickVisibleButton(".mcww-save-button");
    }
    if (event.code === "Escape") {
        globalExitFullscreenIfExists();
        closeSidebarOnMobile();
    }

    if (document.activeElement.matches('textarea, input[type="text"')) {
        return;
    }

    if (event.code === "KeyR") {
        clickVisibleButton(".mcww-refresh");
    }
    if (event.code === "KeyQ") {
        clickVisibleButton(".mcww-queue");
    }
    if (event.code === "KeyH") {
        clickVisibleButton(".mcww-helpers-button");
    }
    if (event.code === "KeyP") {
        ensureProjectIsSelected();
    }
    if (event.code === "KeyO") {
        clickVisibleButton(".mcww-options-button");
    }
    if (event.altKey) {
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
        const tabNumber = parseInt(event.code.replace(/Digit|Numpad/g, ""));
        trySelectTab(tabNumber);
    }
    if (event.code === "KeyS") {
        clickVisibleButton('button.mcww-swap, .mcww-swap input');
    }
    const opacityDiff = 0.03;
    if (event.code === "Equal" || event.code == "NumpadAdd") {
        tryModifySlider(+opacityDiff, '.opacity-slider input[type="range"]');
    }
    if (event.code === "Minus" || event.code == "NumpadSubtract") {
        tryModifySlider(-opacityDiff, '.opacity-slider input[type="range"]');
    }

    const lastMouseEvent = getLastMouseEvent();
    const elementUnderCursor = document.elementFromPoint(lastMouseEvent.clientX, lastMouseEvent.clientY);
    let container = null;
    if (elementUnderCursor) {
        container = elementUnderCursor.closest('.gallery-container, .image-container, .video-container');
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
            if (event.ctrlKey) {
                container.querySelector('button.copy')?.click();
            } else {
                container.querySelector('button.compare')?.click();
            }
        }

        if (event.ctrlKey && event.code === "KeyV") {
            container.querySelector('button.paste')?.click();
        }

        if (event.code == "Space") {
            const video = container.querySelector('video');
            if (video) {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
                event.preventDefault();
            }
        }

    }

    // image editor tab
    const editor = document.querySelector(".helpers-editor");

    if (editor && uiElementIsVisible(editor)) {
        if (event.code === "Equal" || event.code == "NumpadAdd") {
            editor.querySelector('button[title="Zoom in"]')?.click();
        }
        if (event.code === "Minus" || event.code == "NumpadSubtract") {
            editor.querySelector('button[title="Zoom out"]')?.click();
        }
        if (event.code === "Space") {
            const panButton = editor.querySelector('button[title="Pan"]');
            if (panButton) {
                panButton.click();
                event.preventDefault();
            }
        }
        if (event.code === "KeyZ" && event.ctrlKey) {
            if (!event.shiftKey) {
                editor.querySelector('button[title="Undo"]')?.click();
            } else {
                editor.querySelector('button[title="Redo"]')?.click();
            }
        }
        if (event.code === "KeyY" && event.ctrlKey) {
            editor.querySelector('button[title="Redo"]')?.click();
        }
        if (event.code === 'BracketLeft' || event.code === 'BracketRight') {
            const brushSizeButton = editor.querySelector('button[title="Brush Size"]');
            if (brushSizeButton) {
                brushSizeButton.click();
                const brushSizeDiff = 2;
                const brushSizeSliderSelector = '.helpers-editor input[type="range"]';
                waitForElement(brushSizeSliderSelector, () => {
                    if (event.code === 'BracketRight') {
                        tryModifySlider(brushSizeDiff, brushSizeSliderSelector);
                    } else {
                        tryModifySlider(-brushSizeDiff, brushSizeSliderSelector);
                    }
                })
            }
        }
        if (event.ctrlKey && event.code === "KeyV") {
            document.querySelector('.editor-input-image button.paste')?.click();
        }
    }
});


document.addEventListener('keyup', (event) => {
    // image editor tab
    const editor = document.querySelector(".helpers-editor");

    if (editor && uiElementIsVisible(editor)) {
        if (event.code === "Space") {
            const brushButton = editor.querySelector('button[title="Brush"]');
            if (brushButton) {
                brushButton.click();
                event.preventDefault();
            }
        }
    }
});
