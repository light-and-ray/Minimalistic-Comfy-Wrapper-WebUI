
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
        tryModifyOpacity(+opacityDiff);
    }
    if (event.code === "Minus" || event.code == "NumpadSubtract") {
        tryModifyOpacity(-opacityDiff);
    }

    const lastMouseEvent = getLastMouseEvent();
    const elementUnderCursor = document.elementFromPoint(lastMouseEvent.clientX, lastMouseEvent.clientY);
    let container = null;
    if (elementUnderCursor) {
        container = elementUnderCursor.closest('.gallery-container, .image-container, .video-container');
    }

    if (container) {
        if (event.code === "KeyS") {
            const downloadButton = container.querySelector('button[title="Download"]');
            if (downloadButton) {
                downloadButton.click();
            }
        }

        if (event.code === "KeyF") {
            const fullscreenButton = container.querySelector('button[title="Exit fullscreen mode"], button[title="Fullscreen"]');
            if (fullscreenButton) {
                fullscreenButton.click();
            }
        }

        if (event.code === "KeyA") {
            const toAButton = container.querySelector('button.to-a');
            if (toAButton) {
                toAButton.click();
            }
        }

        if (event.code === "KeyB") {
            const toBButton = container.querySelector('button.to-b');
            if (toBButton) {
                toBButton.click();
            }
        }

        if (event.code === "KeyC") {
            if (event.ctrlKey) {
                const copyButton = container.querySelector('button.copy');
                if (copyButton) {
                    copyButton.click();
                }
            } else {
                const compareButton = container.querySelector('button.compare');
                if (compareButton) {
                    compareButton.click();
                }
            }
        }

        if (event.ctrlKey && event.code === "KeyV") {
            const pasteButton = container.querySelector('button.paste');
            if (pasteButton) {
                pasteButton.click();
            }
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
});


