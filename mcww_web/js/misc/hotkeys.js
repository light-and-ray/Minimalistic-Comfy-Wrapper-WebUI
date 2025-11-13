
function clickVisibleButton(selector) {
    const buttons = document.querySelectorAll(selector);
    for (const button of buttons) {
        if (uiElementIsVisible(button) && uiElementInSight(button)) {
            button?.click();
            return;
        }
    }
}

document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.code === "Enter") {
        clickVisibleButton('.mcww-run-button');
    }

    if (["TEXTAREA"].includes(document.activeElement.tagName)) {
        return;
    }
    if (event.ctrlKey && !event.shiftKey && event.code === "KeyS") {
        event.preventDefault();
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
    if (!event.ctrlKey && event.code === "Enter") {
        clickVisibleButton('.mcww-run-button');
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
    }
});


