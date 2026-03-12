

function legacyContextMenuHandler(event) {
    if (!isInsidePWA()) {
        return;
    }
    if (event.shiftKey) {
        return;
    }
    if (event.target.matches('a, img, video, audio, '
                        + 'textarea:not([disabled]), '
                        + 'input[type="text"]:not([disabled]), '
                        + 'input[type="number"]:not([disabled]), '
                        + 'input:not([type]):not([disabled]), '
                        + 'div.cm-content[contenteditable="true"] *')
        && !e.target.closest(".no-pwa-context-menu"))
    {
        return;
    }
    const selection = window.getSelection();
    const selectedText = selection.toString();
    if (selectedText.length > 0) {
        return;
    }
    event.preventDefault();
}


let g_lastWasMouse = false;
window.addEventListener('mousedown', () => {
    g_lastWasMouse = true;
});
window.addEventListener('touchstart', () => {
    g_lastWasMouse = false;
});


document.addEventListener('contextmenu', (event) => {
    if ((event.pointerType === "touch" && event.target.matches(".no-touch-context-menu")
                        || event.target.closest(".no-touch-context-menu"))) {
        event.preventDefault();
        return;
    }
    if (!OPTIONS.useCustomContextMenu) {
        return legacyContextMenuHandler(event);
    }
    if (event.shiftKey) {
        return;
    }
    if (event.target.matches(
        'textarea:not([disabled]), '
        + 'input[type="text"]:not([disabled]), '
        + 'input[type="number"]:not([disabled]), '
        + 'input:not([type]):not([disabled]), '
        + 'div.cm-content[contenteditable="true"] *')
    ) {
        return;
    }
    if (!g_lastWasMouse) {
        const selection = window.getSelection();
        const selectedText = selection.toString();
        if (selectedText.length > 0) {
            return;
        }
    }

    const gallerySelector = '.gallery-container, .image-container, .video-container, .mcww-other-gallery, .upload-gallery';
    let gallery = null;
    if (event.target.matches(gallerySelector)) {
        gallery = event.target;
    } else {
        gallery = event.target.closest(gallerySelector);
    }
    if (!isInsidePWA()) {
        if (!gallery && !event.target.matches("a, img, video")) {
            return;
        }
    }
    new McwwContextMenu(gallery, event);
    event.preventDefault();
});
