
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
    if (isTrueContextMenu) {
        event.preventDefault();
    }
    const menuItem = event.target.closest('.mcww-context-menu .menu-item');
    if (isTrueContextMenu && menuItem) {
        menuItem.click();
        return;
    }
    new McwwContextMenu(gallery, event);
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


onUiLoaded(() => {

class McwwContextMenu extends McwwMenuBase {
    constructor(gallery, event) {
        super(event, { className: 'mcww-context-menu', relaxed: false });
        this.gallery = gallery;
        this.target = event.target;
        const selection = window.getSelection();
        this.selectedText = selection ? selection.toString().trim() : '';
        this.hasDownload = false;
        this.init();
    }

    init() {
        this.buildGallerySection();
        this.buildPasteSection();
        this.buildLinkSection();
        this.buildUrlSection();
        this.buildSelectionSection();
        if (this.menu.children.length > 0) {
            this.render();
        }
    }

    buildSelectionSection() {
        if (this.selectedText) {
            this.menu.appendChild(this.createItem(MCWW.SVG["copy"], `Copy "${truncateMiddle(this.selectedText, 25)}"`, () => {
                copyTextToClipboard(this.selectedText);
                mouseAlert("Copied");
            }));
        }
    }

    buildGallerySection() {
        if (!this.gallery) return;
        const buttons = this.gallery.querySelectorAll('.icon-button-wrapper > *:not([disabled])');
        buttons.forEach(button => {
            if (!uiElementIsVisible(button)) return;
            const iconContent = button.innerHTML;
            let label = null;
            if (button.matches(".icon-button")) {
                label = button.title;
            } else {
                label = button.querySelector(".icon-button")?.title;
            }
            if (button.classList.contains("paste")) {
                return;
            }
            if (label.toLowerCase().includes("download")) {
                this.hasDownload = true;
            }
            if (label === "common.upload") {
                label = "Add more files";
                button = button.querySelector("button");
            }
            const item = this.createItem(iconContent, label, () => button.click());
            this.menu.appendChild(item);
        });
    }

    buildPasteSection() {
        if (OPTIONS.maxClipboardHistoryLength > 0) {
            const item = this.createItem(MCWW.SVG["clipboardHistory"], "Open Clipboard History", () => {
                new McwwClipboardHistoryMenu(this.event);
            });
            this.menu.appendChild(item);
        }
        if (this.gallery) {
            const button = this.gallery.querySelector('button.paste');
            if (uiElementIsVisible(button)) {
                const item = this.createItem(MCWW.SVG["clipboard"], "Paste from Clipboard", () => button.click());
                this.menu.appendChild(item);
            }
        }
    }

    buildUrlSection() {
        let element = this.target;
        if (!this.target.matches('a, img, video') && this.gallery) {
            element = this.gallery.querySelector('img, video');
        }
        if (!element) {
            return;
        }
        let url = element?.src || element?.href;
        if (!url && this.gallery) {
            url = this.gallery.querySelector("a.download-link")?.href;
        }
        if (url) {
            let text = (isInsidePWA() ? 'Open in Browser' : 'Open in New Tab');
            this.menu.appendChild(this.createItem('🡒', text, () => {
                window.open(url, '_blank');
            }));

            if (element.matches("img") && navigator.clipboard) {
                const item = this.createItem("⇦", 'Copy to Sys. Clipboard', () => {
                    try {
                        copyImageToSystemClipboard(url)
                        mouseAlert("Image Copied", 900);
                    } catch (err) {
                        grError("Failed to copy");
                        console.error("Failed to copy: ", err);
                    }
                });
                this.menu.appendChild(item);
            }

            if (!this.hasDownload && element.matches("img, video")) {
                const item = this.createItem('⇩', 'Download file from URL', () => {
                    downloadFileByUrl(url);
                    mouseAlert("Downloading...", 900);
                });
                this.menu.appendChild(item);
                this.hasDownload = true;
            }

            const item = this.createItem(MCWW.SVG["link"], 'Copy URL', () => {
                copyTextToClipboard(url);
                mouseAlert("URL Copied", 900);
            });
            this.menu.appendChild(item);
        }
    }

    buildLinkSection() {
        const anchor = this.target.closest('a');
        if (anchor && anchor.href) {
            const url = anchor.href;
            this.menu.appendChild(this.createItem('🡕', 'Open in New Window', () => {
                window.open(url, '_blank', 'popup=yes');
            }));
        }
    }
}

window.McwwContextMenu = McwwContextMenu;

});
