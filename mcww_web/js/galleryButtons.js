
// paste button


function fixClipboardPaste(updatedElements) {
    const imageContainers = updatedElements.querySelectorAll('.image-container');
    imageContainers.forEach(container => {
        if (container.dataset.clipboardFixAttached) return;
        const pasteButton = container.querySelector('.source-selection > button:nth-of-type(3)');
        if (pasteButton) {
            const newPasteButton = pasteButton.cloneNode(true);
            pasteButton.parentNode.replaceChild(newPasteButton, pasteButton);
            newPasteButton.classList.add("paste");
            newPasteButton.onclick = async () => {
                try {
                    mouseAlert("Pasting...");
                    const dropButton = container.querySelector('.upload-container > button');
                    await dropImageFromClipboard(dropButton);
                } catch (error) {
                    const text = `Failed to paste image: ${error}`;
                    console.error(text);
                    grError(text);
                }
            }
        }
        container.dataset.clipboardFixAttached = "true";
    });

    const galleries = updatedElements.querySelectorAll('.gallery-container:not(:has(button.paste))');
    galleries.forEach((container) => {
        if (container.parentElement.classList.contains("no-paste")) {
            return;
        }
        const uploadToolButton = container.querySelector('button[title="common.upload"]');
        if (uploadToolButton) {
            const pasteButton = uploadToolButton.cloneNode(false);
            pasteButton.classList.add("paste");
            pasteButton.classList.add("force-text-style");
            pasteButton.classList.add("gallery-button");
            pasteButton.textContent = "📋";
            pasteButton.title = "Paste from clipboard";
            pasteButton.onclick = async () => {
                try {
                    mouseAlert("Pasting...");
                    const dropButton = uploadToolButton.querySelector('button:has(>input)');
                    await dropImageFromClipboard(dropButton);
                } catch (error) {
                    const text = `Failed to paste image: ${error}`;
                    console.error(text);
                    grError(text);
                }
            };
            uploadToolButton.parentNode.insertBefore(pasteButton, uploadToolButton);
        }
    });

    const uploadGalleries = updatedElements.querySelectorAll('.upload-gallery:not(:has(button.paste))');
    uploadGalleries.forEach((container) => {
        if (container.classList.contains("no-paste")) {
            return;
        }
        const emptyUploadButton = container.querySelector("&>button");
        if (emptyUploadButton) {
            const pasteButton = document.createElement('button');
            pasteButton.classList.add("paste", "force-text-style", "mcww-text-button");
            pasteButton.textContent = "Paste";
            pasteButton.title = "Paste from clipboard";
            pasteButton.onclick = async () => {
                try {
                    mouseAlert("Pasting...");
                    const uploadButton = container.querySelector("&>button:not(.paste)")
                    await dropImageFromClipboard(uploadButton);
                } catch (error) {
                    const text = `Failed to paste image: ${error}`;
                    console.error(text);
                    grError(text);
                }
            };
            emptyUploadButton.parentNode.insertBefore(pasteButton, emptyUploadButton);
        }
    });


}

onUiUpdate(fixClipboardPaste);


// camera buttons


function isCameraActive() {
    const containers = document.querySelectorAll('.image-container, .video-container');
    for (container of containers) {
        const cameraButton = container.querySelector('button.camera-button.selected');
        const video = container.querySelector('video');
        if (video && uiElementIsVisible(video) && cameraButton) {
            return true;
        }
    }
    return false;
}


function fixCameraButtons(updatedElements) {
    const containers = updatedElements.querySelectorAll('.image-container, .video-container');
    containers.forEach(container => {
        if (container.dataset.cameraFixAttached) return;
        const cameraButton = container.querySelector('.source-selection > button:nth-of-type(2)');
        if (cameraButton) {
            cameraButton.classList.add("camera-button");
        }
        container.dataset.cameraFixAttached = "true";
    });
}

onUiUpdate(fixCameraButtons);


// compare and copy buttons


function attachGalleryButtons(updatedElements) {
    const containers = updatedElements.querySelectorAll('.gallery-container, .image-container');
    containers.forEach(container => {
        if (container.querySelector('.gallery-button')) return;
        if (!container.parentElement) return;
        let needCompare = true;
        let needCopy = true;

        if (container.parentElement.classList.contains("no-compare")) {
            needCompare = false;
        }
        if (container.parentElement.classList.contains("no-copy")) {
            needCopy = false;
        }

        const fullscreenButton = container.querySelector('button[title="Fullscreen"]');
        if (!fullscreenButton) return;
        const firstSibling = fullscreenButton.parentNode.childNodes[0];

        if (needCopy) {
            const copyButton = fullscreenButton.cloneNode(false);
            copyButton.textContent = "⎘";
            copyButton.title = "Copy to Clipboard";
            copyButton.classList.add("gallery-button");
            copyButton.classList.add("copy");
            copyButton.onclick = () => {
                const img = container.querySelector("img");
                if (img) {
                    copyImageToClipboard(img);
                    mouseAlert("Image copied to clipboard");
                }
            };

            fullscreenButton.parentNode.insertBefore(copyButton, firstSibling);
        }

        if (needCompare) {
            const compareButton = fullscreenButton.cloneNode(false);
            compareButton.textContent = "A|B";
            compareButton.title = "Compare";
            compareButton.classList.add("gallery-button");
            compareButton.classList.add("compare");
            compareButton.onclick = () => openComparePage();

            const toAButton = fullscreenButton.cloneNode(false);
            toAButton.textContent = "🡒A";
            toAButton.title = "Set as Image A";
            toAButton.classList.add("gallery-button");
            toAButton.classList.add("to-a");
            toAButton.onclick = () => {
                const img = container.querySelector("img");
                if (img) {
                    globalCompareImageA = img.src;
                    mouseAlert("Image set as Image A");
                }
            };

            const toBButton = fullscreenButton.cloneNode(false);
            toBButton.textContent = "🡒B";
            toBButton.title = "Set as Image B";
            toBButton.classList.add("gallery-button");
            toBButton.classList.add("to-b");
            toBButton.onclick = () => {
                const img = container.querySelector("img");
                if (img) {
                    globalCompareImageB = img.src;
                    mouseAlert("Image set as Image B");
                }
            };

            fullscreenButton.parentNode.insertBefore(compareButton, firstSibling);
            fullscreenButton.parentNode.insertBefore(toAButton, firstSibling);
            fullscreenButton.parentNode.insertBefore(toBButton, firstSibling);
        }
    });
}

onUiUpdate(attachGalleryButtons);

