

async function copyImageToClipboard(img) {
    setBrowserStorageVariable("imageClipboardContent", img.src)
}


async function dropImageFromClipboard(dropButton) {
    const imageClipboardContent = getBrowserStorageVariable('imageClipboardContent');
    if (!imageClipboardContent) {
        grInfo("No data in clipboard. Important: only images copied on the host by using ⎘ button are possible to paste");
        return;
    }
    try {
        const file = await imgUrlToFile(imageClipboardContent);
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        const dropEvent = new DragEvent('drop', {
            dataTransfer: dataTransfer,
            bubbles: true,
            cancelable: true,
        });
        dropButton.dispatchEvent(dropEvent);
    } catch (error) {
        console.error("Failed to drop image:", error);
        grError("Failed to drop image. See console for details.");
    }
}

