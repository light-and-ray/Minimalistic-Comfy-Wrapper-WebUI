
class McwwMenuBase {
    constructor(event, options = {}) {
        this.event = event;
        this.options = {
            relaxed: false,
            className: 'mcww-menu',
            containerSelector: 'main',
            ...options
        };
        this.closeHandler = null;
        this.removeExisting();

        this.menu = document.createElement('div');
        this.menu.classList.add('mcww-menu', this.options.className);
    }


    createItem(iconHtml, text, action) {
        const item = document.createElement('div');
        item.className = 'menu-item';

        const iconSpan = document.createElement('span');
        iconSpan.className = 'icon';
        iconSpan.innerHTML = iconHtml;

        const textSpan = document.createElement('span');
        textSpan.className = 'text';
        textSpan.textContent = text || "Action";

        item.appendChild(iconSpan);
        item.appendChild(textSpan);

        item.addEventListener('click', (e) => {
            e.stopPropagation();
            action();
            this.destroy();
        });
        return item;
    }


    render() {
        const container = document.querySelector(this.options.containerSelector) || document.body;
        container.appendChild(this.menu);

        const viewport = window.visualViewport || {
            scale: 1,
            offsetLeft: 0,
            offsetTop: 0,
            width: window.innerWidth,
            height: window.innerHeight
        };
        let invScale = 1 / viewport.scale;
        if (this.event.pointerType === "touch") {
            invScale *= 1.2;
        }

        const { clientX: x, clientY: y } = this.event;
        let { width, height } = getFullElementSize(this.menu);
        height *= invScale;
        width *= invScale;

        const minX = viewport.offsetLeft;
        const maxX = viewport.offsetLeft + viewport.width;
        const minY = viewport.offsetTop;
        const maxY = viewport.offsetTop + viewport.height;

        let posX, posY;

        // Horizontal Logic (Standard Flip)
        // We check against the actual right edge of the viewport (maxX)
        posX = (x + width > maxX) ? x - width : x;
        posX = clamp(posX, minX, maxX - width);

        // Vertical Logic: Relaxed vs Strict
        if (this.options.relaxed) {
            // Pull toward center based on cursor position relative to the visible viewport
            const bias = (y - minY) / viewport.height;
            posY = y - (height * bias);
        } else {
            // Standard Flip checking against bottom edge (maxY)
            posY = (y + height > maxY) ? y - height : y;
        }
        posY = clamp(posY, minY, maxY - height);

        this.menu.style.left = `${posX}px`;
        this.menu.style.top = `${posY}px`;
        this.menu.style.transform = `scale(${invScale})`;
        this.menu.style.maxHeight = `calc(${viewport.height * 0.8}px / ${invScale})`;

        this.setupListeners();
    }


    setupListeners() {
        this.closeHandler = (e) => {
            if (e.type === 'keydown') {
                const modifiers = ['Alt', 'Control', 'Shift', 'Meta'];
                if (modifiers.includes(e.key)) {
                    return;
                }
            }
            if (e.target instanceof VisualViewport || !this.menu.contains(e.target)) {
                this.destroy();
            }
        };
        const opts = { capture: true };
        ['pointerdown', 'keydown', 'scroll'].forEach(type => {
            document.addEventListener(type, this.closeHandler, opts);
        });
        if (window.visualViewport) {
            ['resize', 'scroll'].forEach(type => {
                window.visualViewport.addEventListener(type, this.closeHandler, opts);
            });
        }
    }

    removeExisting() {
        const old = document.querySelector(`.${this.options.className}`);
        if (old) old.remove();
    }

    destroy() {
        this.removeExisting();
        if (this.closeHandler) {
            const opts = { capture: true };
            ['pointerdown', 'keydown', 'scroll'].forEach(type => {
                document.removeEventListener(type, this.closeHandler, opts);
            });
            if (window.visualViewport) {
                ['resize', 'scroll'].forEach(type => {
                    window.visualViewport.removeEventListener(type, this.closeHandler, opts);
                });
            }
            this.closeHandler = null;
        }
    }
}


class McwwContextMenu extends McwwMenuBase {
    constructor(gallery, event) {
        super(event, { className: 'mcww-context-menu', relaxed: false });
        this.gallery = gallery;
        this.target = event.target;
        const selection = window.getSelection();
        this.selectedText = selection ? selection.toString().trim() : '';
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
            this.menu.appendChild(this.createItem(COPY_SVG, `Copy "${truncateMiddle(this.selectedText, 25)}"`, () => {
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
        if (OPTIONS.maxClipboardHistoryLength > 0) {
            const item = this.createItem(CLIPBOARD_HISTORY_SVG, "Open clipboard history", () => {
                new McwwClipboardHistoryMenu(this.event);
            });
            this.menu.appendChild(item);
        }
        if (this.gallery) {
            const button = this.gallery.querySelector('button.paste');
            if (uiElementIsVisible(button)) {
                const item = this.createItem(CLIPBOARD_SVG, "Paste from Clipboard", () => button.click());
                this.menu.appendChild(item);
            }
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
}


class McwwClipboardHistoryMenu extends McwwMenuBase {
    constructor(event) {
        super(event, { className: 'clipboard-history-menu', relaxed: true });
        this.init();
    }

    init() {
        const current = getBrowserStorageVariable("mediaClipboardContent") ?? "Clipboard is empty";
        const history = getBrowserStorageVariable("mediaClipboardContent_history", []);
        this.menu.appendChild(this.createHistoryItem(current, () => {}, "current"));
        history.forEach(url => {
            this.menu.appendChild(this.createHistoryItem(url, () => {
                copyMediaToClipboard(url);
                mouseAlert("Copied from history", 700);
            }));
        });
        this.render();
    }

    createHistoryItem(text, action, type = null) {
        let iconHtml = '';
        if (isImageUrl(text)) {
            iconHtml = `<img src="${text}" style="width:100%; height:100%; object-fit:cover;">`;
        } else if (isVideoUrl(text)) {
            iconHtml = `<video src="${text}" muted style="width:100%; height:100%; object-fit:cover;"></video>`;
        } else {
            iconHtml = isAudioUrl(text) ? '🎵' : '📋';
        }
        let baseName = getBasename(decodeURIComponent(text));
        if (type === "current") {
            baseName = "★ " + baseName;
        }
        text = truncateMiddle(baseName, 25);

        const item = this.createItem(iconHtml, text, action);

        item.classList.add('history-item');
        if (type === "current") item.classList.add("current");

        const iconSpan = item.querySelector('.icon');
        iconSpan.classList.add('preview-wrapper');

        const textSpan = item.querySelector('.text');
        textSpan.title = baseName;

        return item;
    }
}

