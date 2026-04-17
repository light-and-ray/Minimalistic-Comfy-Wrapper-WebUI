

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
    return await dropMediaContent(dropButton, mediaClipboardContent)
}


async function dropMediaContent(dropButton, mediaContent) {
    try {
        let file = null;
        if (isImageUrl(mediaContent)) {
            file = await imgUrlToFile(mediaContent);
        } else {
            file = await fileUrlToFile(mediaContent);
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

