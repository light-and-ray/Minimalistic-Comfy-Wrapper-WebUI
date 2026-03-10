

class McwwContextMenu {
    constructor(gallery, event) {
        event.preventDefault();
        this.gallery = gallery;
        this.event = event;
        this.target = event.target;
        this.menu = null;
        const selection = window.getSelection();
        this.selectedText = selection ? selection.toString().trim() : '';
        this.init();
    }

    init() {
        this.removeExisting();
        this.menu = document.createElement('div');
        this.menu.classList.add('mcww-menu', 'mcww-context-menu');
        this.buildGallerySection();
        this.buildPasteSection();
        this.buildLinkSection();
        this.buildUrlSection();
        this.buildSelectionSection();
        if (this.menu.children.length > 0) {
            this.render();
        }
    }

    createItem(iconHtml, text, action) {
        const item = document.createElement('div');
        item.className = 'menu-item';
        const iconSpan = document.createElement('span');
        const textSpan = document.createElement('span');
        iconSpan.className = 'icon';
        iconSpan.innerHTML = iconHtml;
        textSpan.className = 'text';
        textSpan.textContent = text || "Action";
        item.appendChild(iconSpan);
        item.appendChild(textSpan);
        item.addEventListener('click', () => {
            action();
            this.destroy();
        });
        return item;
    }

    buildSelectionSection() {
        if (this.selectedText) {
            this.menu.appendChild(this.createItem('⎘', `Copy "${truncateString(this.selectedText, 25)}"`, () => {
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
            if (label === "common.upload") {
                label = "Add more files";
                button = button.querySelector("button");
            }
            const item = this.createItem(iconContent, label, () => button.click());
            this.menu.appendChild(item);
        });
    }

    buildPasteSection() {
        if (this.gallery) {
            const button = this.gallery.querySelector('button.paste');
            if (uiElementIsVisible(button)) {
                const item = this.createItem(CLIPBOARD_SVG, "Paste from Clipboard", () => button.click());
                this.menu.appendChild(item);
            }
        }
        if (OPTIONS.maxClipboardHistoryLength > 0) {
            const item = this.createItem(CLIPBOARD_HISTORY_SVG, "Open clipboard history", () => {
                new McwwClipboardHistoryMenu(this.event);
            });
            this.menu.appendChild(item);
        }
    }

    buildUrlSection() {
        let element = this.target;
        if (!this.target.matches('a, img, video') && this.gallery) {
            element = this.gallery.querySelector('img, video');
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
            const item = this.createItem(LINK_SVG, 'Copy URL', () => {
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

    render() {
        document.querySelector('main').appendChild(this.menu);

        const { clientX: x, clientY: y } = this.event;
        const menuRect = this.menu.getBoundingClientRect();

        let posX = x;
        let posY = y;
        const { width, height } = getFullElementSize(this.menu);
        if (x + width > window.innerWidth) {
            posX = x - width;
        }
        if (y + height > window.innerHeight) {
            posY = y - height;
        }
        posX = Math.max(0, posX);
        posY = Math.max(0, posY);

        this.menu.style.left = `${posX}px`;
        this.menu.style.top = `${posY}px`;

        this.closeHandler = this.handleOutsideClick.bind(this);

        document.addEventListener('pointerdown', this.closeHandler, { capture: true });
        document.addEventListener('keydown', this.closeHandler);
        document.addEventListener('scroll', this.closeHandler);
    }

    handleOutsideClick(e) {
        if (this.menu && !this.menu.contains(e.target)) {
            this.destroy();
        }
    }

    removeExisting() {
        const oldMenu = document.querySelector('.mcww-context-menu');
        if (oldMenu) {
            oldMenu.remove();
        }
    }

    destroy() {
        this.removeExisting();
        if (this.closeHandler) {
            document.removeEventListener('pointerdown', this.closeHandler, { capture: true });
            document.removeEventListener('keydown', this.closeHandler);
            document.removeEventListener('scroll', this.closeHandler);
            this.closeHandler = null;
        }
    }
}


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
    if (!OPTIONS.useCustomContextMenu) {
        return legacyContextMenuHandler(event);
    }
    if (event.shiftKey) {
        return;
    }
    if (event.target.matches(
        'textarea:not([disabled]), '
        + 'input[type="text"]:not([disabled]), '
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
});
