

function legacyContextMenuHandler(event) {
    if (!isInsidePWA()) {
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


function _mcwwContextMenuListener(event) {
    const isTrueContextMenu = event.type === "contextmenu";
    const gallerySelector = '.gallery-container, .image-container, .video-container, .mcww-other-gallery, .upload-gallery';
    let gallery = null;
    if (event.target.matches(gallerySelector)) {
        gallery = event.target;
    } else {
        gallery = event.target.closest(gallerySelector);
    }
    if (isTrueContextMenu && !isInsidePWA()) {
        if (!gallery && !event.target.matches("a, img, video")) {
            return;
        }
    }
    new McwwContextMenu(gallery, event);
    if (isTrueContextMenu) {
        event.preventDefault();
    }
}


let g_lastWasMouse = true;
window.addEventListener('pointerdown', (event) => {
    g_lastWasMouse = (event.pointerType !== "touch");
});


document.addEventListener('contextmenu', (event) => {
    if (event.shiftKey) {
        return;
    }
    if (event.pointerType === "touch" && event.target.matches(".no-touch-context-menu *, .no-touch-context-menu")) {
        event.preventDefault();
        return;
    }
    if (!OPTIONS.useCustomContextMenu) {
        return legacyContextMenuHandler(event);
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
    _mcwwContextMenuListener(event);
});


(function() {
    if (!OPTIONS.useCustomContextMenu) {
        return;
    }
    let touchStartTime = 0;
    let initialTouches = [];
    const TAP_THRESHOLD = 300; // ms
    const MOVE_THRESHOLD = 10;

    document.addEventListener('touchstart', (e) => {
        if (e.touches.length === 2) {
            touchStartTime = Date.now();
            initialTouches = Array.from(e.touches).map(t => ({
                id: t.identifier,
                x: t.clientX,
                y: t.clientY
            }));
        } else {
            touchStartTime = 0;
            initialTouches = [];
        }
    }, { passive: false });

    document.addEventListener('touchend', (e) => {
        const duration = Date.now() - touchStartTime;
        if (touchStartTime > 0 && duration < TAP_THRESHOLD) {
            const finalTouches = Array.from(e.touches).concat(Array.from(e.changedTouches));
            const uniqueTouches = Array.from(new Map(finalTouches.map(t => [t.identifier, t])).values());
            if (uniqueTouches.length === 2 && initialTouches.length === 2) {
                const hasMoved = uniqueTouches.some(tEnd => {
                    const tStart = initialTouches.find(t => t.id === tEnd.identifier);
                    if (!tStart) return true; // Shouldn't happen, but safety first
                    const dist = Math.sqrt(
                        Math.pow(tEnd.clientX - tStart.x, 2) +
                        Math.pow(tEnd.clientY - tStart.y, 2)
                    );
                    return dist > MOVE_THRESHOLD;
                });

                if (!hasMoved) {
                    const x0 = uniqueTouches[0].clientX;
                    const x1 = uniqueTouches[1].clientX;
                    const y0 = uniqueTouches[0].clientY;
                    const y1 = uniqueTouches[1].clientY;

                    let lowestFingerX, lowestFingerY, highestFingerX, highestFingerY;

                    if (y0 > y1) {
                        lowestFingerX = x0;
                        lowestFingerY = y0;
                        highestFingerX = x1;
                        highestFingerY = y1;
                    } else {
                        lowestFingerX = x1;
                        lowestFingerY = y1;
                        highestFingerX = x0;
                        highestFingerY = y0;
                    }

                    const targetX = highestFingerX + (lowestFingerX - highestFingerX) * 0.35;
                    const targetY = highestFingerY + (lowestFingerY - highestFingerY) * 0.35;
                    const syntheticEvent = {
                        type: "touchend",
                        target: document.elementFromPoint(targetX, targetY),
                        pointerType: "touch",
                        clientX: targetX,
                        clientY: targetY,
                        preventDefault: () => e.preventDefault(),
                        stopPropagation: () => e.stopPropagation()
                    };

                    _mcwwContextMenuListener(syntheticEvent);
                }
            }
        }
        // Reset state
        touchStartTime = 0;
        initialTouches = [];
    }, { passive: false });
})();
