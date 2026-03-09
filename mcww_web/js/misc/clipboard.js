
class McwwClipboardHistoryMenu {
    constructor(event) {
        this.event = event;
        this.menu = null;
        this.init();
    }

    init() {
        this.removeExisting();
        const current = getBrowserStorageVariable("mediaClipboardContent", "Clipboard is empty");
        const history = getBrowserStorageVariable("mediaClipboardContent_history", []);

        this.menu = document.createElement('div');
        this.menu.classList.add('mcww-menu', 'clipboard-history-menu');

        if (current) {
            this.menu.appendChild(this.createHistoryItem(current, true));
        }
        history.forEach(url => {
            this.menu.appendChild(this.createHistoryItem(url));
        });

        this.render();
    }

    createHistoryItem(url, isCurrent=false) {
        const item = document.createElement('div');
        item.classList.add('menu-item', 'history-item');
        if (isCurrent) {
            item.classList.add("current");
        }

        const previewWrapper = document.createElement('span');
        previewWrapper.className = 'icon preview-wrapper';

        // Determine preview content based on URL type
        if (isImageUrl(url)) {
            const img = document.createElement('img');
            img.src = url;
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'cover';
            previewWrapper.appendChild(img);
        } else if (isVideoUrl(url)) {
            const video = document.createElement('video');
            video.src = url;
            video.muted = true;
            video.style.width = '100%';
            video.style.height = '100%';
            video.style.objectFit = 'cover';
            previewWrapper.appendChild(video);
        } else if (isAudioUrl(url)) {
            previewWrapper.innerHTML = '🎵';
        } else {
            previewWrapper.innerHTML = '📋';
        }

        const textSpan = document.createElement('span');
        textSpan.className = 'text';
        let baseName = getBasename(decodeURIComponent(url));
        if (isCurrent) {
            baseName = "★ " + baseName;
        }
        textSpan.textContent = truncateString(baseName, 25);
        textSpan.title = baseName;

        item.appendChild(previewWrapper);
        item.appendChild(textSpan);

        item.addEventListener('click', () => {
            if (!isCurrent) {
                copyMediaToClipboard(url);
                mouseAlert("Copied from history", 700);
            }
            this.destroy();
        });

        return item;
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

        this.closeHandler = (e) => {
            if (this.menu && !this.menu.contains(e.target)) {
                this.destroy();
            }
        };

        document.addEventListener('pointerdown', this.closeHandler, { capture: true });
        document.addEventListener('keydown', this.closeHandler);
    }

    removeExisting() {
        const oldMenu = document.querySelector('.clipboard-history-menu');
        if (oldMenu) oldMenu.remove();
    }

    destroy() {
        this.removeExisting();
        if (this.closeHandler) {
            document.removeEventListener('pointerdown', this.closeHandler, { capture: true });
            document.removeEventListener('keydown', this.closeHandler);
            this.closeHandler = null;
        }
    }
}


function copyMediaToClipboard(media) {
    const old = getBrowserStorageVariable("mediaClipboardContent");
    let src = media?.src;
    if (!src) src = media?.href;
    if (!src) src = media;
    setBrowserStorageVariable("mediaClipboardContent", src);

    if (old && !old.startsWith('blob:')) {
        let history = getBrowserStorageVariable("mediaClipboardContent_history", []);
        history.unshift(old);
        history = history.filter(item => item !== src);
        if (history.length > OPTIONS.maxClipboardHistoryLength) {
            history = history.slice(0, OPTIONS.maxClipboardHistoryLength);
        }
        setBrowserStorageVariable("mediaClipboardContent_history", history);
    }
}


async function dropMediaFromClipboard(dropButton) {
    const mediaClipboardContent = getBrowserStorageVariable('mediaClipboardContent');
    if (!mediaClipboardContent) {
        grInfo("No data in clipboard. Important: only files copied on the same host by using ⎘ button are possible to paste");
        return;
    }
    try {
        let file = null;
        if (isImageUrl(mediaClipboardContent)) {
            file = await imgUrlToFile(mediaClipboardContent);
        } else {
            file = await fileUrlToFile(mediaClipboardContent);
        }
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        const dropEvent = new DragEvent('drop', {
            dataTransfer: dataTransfer,
            bubbles: true,
            cancelable: true,
        });
        dropButton.dispatchEvent(dropEvent);
    } catch (error) {
        console.error("Failed to drop file:", error);
        grError("Failed to drop file. See console for details.");
    }
}

