

function copyMediaToClipboard(media, blobFileName=null) {
    const old = getBrowserStorageVariable("mediaClipboardContent");
    let src = media?.src;
    if (!src) src = media?.href;
    if (!src) src = media;
    setBrowserStorageVariable("mediaClipboardContent", src);
    if (src.startsWith('blob:')) {
        setSessionStorageVariable("tmpBlobFileName", blobFileName);
    }

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
    return await dropMediaContent(dropButton, mediaClipboardContent)
}


async function dropMediaContent(dropButton, mediaContent) {
    try {
        const file = await fileUrlToFile(mediaContent);
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


function copyTextToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text);
    } else {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        textArea.style.top = "0";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
    }
}


async function copyImageToSystemClipboard(imageUrl) {
    const item = new ClipboardItem({
        "image/png": (async () => {
            const response = await fetch(imageUrl);
            const blob = await response.blob();
            if (blob.type === 'image/png') {
                return blob;
            }
            return await convertBlobToPng(blob);
        })()
    });
    await navigator.clipboard.write([item]);
}


onUiLoaded(() => {
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
            if (OPTIONS.showItemOpenFileFromSystemClipboard && navigator?.clipboard?.read) {
                this.menu.appendChild(this.createOpenFromActualClipboardItem());
            }
            this.render();
        }

        createHistoryItem(text, action, type = null) {
            let iconHtml = '';
            if (isImageUrl(text)) {
                iconHtml = `<img src="${text}" style="width:100%; height:100%; object-fit:cover;">`;
            } else if (isVideoUrl(text)) {
                iconHtml = `<video src="${text}" muted style="width:100%; height:100%; object-fit:cover;"></video>`;
            } else if (isAudioUrl(text)) {
                iconHtml = '🎵';
            } else if (isModel3DUrl(text)) {
                iconHtml = '3D';
            } else {
                iconHtml = '📋';
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

        createOpenFromActualClipboardItem() {
            const item = this.createItem("⇨", "Open file from sys. clipboard", openFileFromSystemClipboard);
            item.classList.add('history-item');
            const iconSpan = item.querySelector('.icon');
            iconSpan.classList.add('preview-wrapper');
            return item;
        }
    }
    window.McwwClipboardHistoryMenu = McwwClipboardHistoryMenu;
});
