
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
    if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
        return;
    }
    const lastMouseEvent = getLastMouseEvent();
    const elementUnderCursor = document.elementFromPoint(lastMouseEvent.clientX, lastMouseEvent.clientY);
    let container = null;

    if (elementUnderCursor) {
        container = elementUnderCursor.closest('.gallery-container, .image-container, .video-container');
    }

    if (event.code === "KeyR") {
        clickVisibleButton(".mcww-refresh");
    }

    if (event.code === "KeyS" && container) {
        if (event.ctrlKey) {
            event.preventDefault();
        }
        const downloadButton = container.querySelector('button[title="Download"]');
        if (downloadButton) {
            downloadButton.click();
        }
    }

    if (event.code === "KeyF" && container) {
        const fullscreenButton = container.querySelector('button[title="Exit fullscreen mode"], button[title="Fullscreen"]');
        if (fullscreenButton) {
            fullscreenButton.click();
        }
    }

    if (event.code === "KeyA" && container) {
        const toAButton = container.querySelector('button.to-a');
        if (toAButton) {
            toAButton.click();
        }
    }

    if (event.code === "KeyB" && container) {
        const toBButton = container.querySelector('button.to-b');
        if (toBButton) {
            toBButton.click();
        }
    }

    if (event.code === "KeyC" && container) {
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

    if (event.code === "KeyV" && container) {
        if (event.ctrlKey) {
            const pasteButton = container.querySelector('button.paste');
            if (pasteButton) {
                pasteButton.click();
            }
        }
    }
});


