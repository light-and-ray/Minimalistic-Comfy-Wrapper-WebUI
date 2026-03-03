

function copyMediaToClipboard(media) {
    let src = media?.src;
    if (!src) src = media?.href;
    if (!src)  src = media;
    setBrowserStorageVariable("mediaClipboardContent", src)
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

