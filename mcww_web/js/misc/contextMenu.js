

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
        this.menu.classList.add('mcww-context-menu');

        this.buildGallerySection();
        this.buildUrlSection();
        this.buildSelectionSection();
        this.buildLinkSection();

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
            textSpan.textContent = text;
            item.appendChild(iconSpan);
            item.appendChild(textSpan);
            item.onclick = (e) => {
            e.stopPropagation();
            action();
            this.removeExisting();
        };
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
        buttons.forEach(btn => {
            if (!uiElementIsVisible(btn)) return;

            const iconContent = btn.innerHTML;
            let label = "Action";
            if (btn.matches(".icon-button")) {
                label = btn.title;
            } else {
                label = btn.querySelector(".icon-button")?.title;
            }
            const item = this.createItem(iconContent, label, () => btn.click());
            this.menu.appendChild(item);
        });
    }

    buildUrlSection() {
        const isLinkable = this.target.matches('img, video, a');
        if (isLinkable) {
            const url = this.target.src || this.target.href;
            if (url) {
                const item = this.createItem('⎘', 'Copy URL', () => {
                    copyTextToClipboard(url);
                    mouseAlert("Copied");
                });
                this.menu.appendChild(item);
            }
        }
    }

    buildLinkSection() {
        const anchor = this.target.closest('a');
        if (anchor && anchor.href) {
            const url = anchor.href;

            this.menu.appendChild(this.createItem('🡒', 'Open in New Tab', () => {
                window.open(url, '_blank');
            }));

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
        if (x + menuRect.width > window.innerWidth) posX = x - menuRect.width;
        if (y + menuRect.height > window.innerHeight) posY = y - menuRect.height;

        this.menu.style.left = `${posX}px`;
        this.menu.style.top = `${posY}px`;

        const close = (e) => {
            if (!this.menu.contains(e.target)) {
                this.removeExisting();
                document.removeEventListener('pointerdown', close, { capture: true });
                document.removeEventListener('keydown', close);
            }
        };

        document.addEventListener('pointerdown', close, { capture: true });
        document.addEventListener('keydown', close);
    }

    removeExisting() {
        const oldMenu = document.querySelector('.mcww-context-menu');
        if (oldMenu) oldMenu.remove();
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


document.addEventListener('contextmenu', (event) => {
    if (!OPTIONS.useCustomContextMenu) {
        return legacyContextMenuHandler(event);
    }
    if (event.shiftKey) {
        return;
    }
    if (event.target.matches(
        + 'textarea:not([disabled]), '
        + 'input[type="text"]:not([disabled]), '
        + 'div.cm-content[contenteditable="true"] *')
    ) {
        return
    }

    const gallerySelector = '.gallery-container, .image-container, .video-container, .mcww-other-gallery, .upload-gallery';
    let gallery = null;
    if (event.target.matches(gallerySelector)) {
        gallery = event.target;
    } else {
        gallery = event.target.closest(gallerySelector);
    }
    new McwwContextMenu(gallery, event);
});
