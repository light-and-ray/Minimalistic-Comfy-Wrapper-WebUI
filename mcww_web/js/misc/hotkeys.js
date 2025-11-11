
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
    if (event.code === "KeyR") {
        clickVisibleButton(".mcww-refresh");
    }
});

