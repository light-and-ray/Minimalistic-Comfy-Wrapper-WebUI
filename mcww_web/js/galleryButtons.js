
// paste and camera buttons


var globalClipboardContent = null;


function fixClipboardPaste() {
    const imageContainers = document.querySelectorAll('.image-container');
    imageContainers.forEach(container => {
        if (container.dataset.clipboardFixAttached) return;
        const pasteButton = container.querySelector('.source-selection > button:nth-of-type(3)');
        if (pasteButton) {
            const newPasteButton = pasteButton.cloneNode(true);
            pasteButton.parentNode.replaceChild(newPasteButton, pasteButton);
            newPasteButton.onclick = () => {
                if (!globalClipboardContent) {
                    grInfo("No data in clipboard. Important: only images copied on the same page by using ⎘ button are possible to paste");
                    return;
                }
                if (globalClipboardContent instanceof File) {
                    try {
                        const dropButton = container.querySelector('.upload-container > button');
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(globalClipboardContent);
                        const dropEvent = new DragEvent('drop', {
                            dataTransfer: dataTransfer,
                            bubbles: true,
                            cancelable: true,
                        });
                        dropButton.dispatchEvent(dropEvent);
                    } catch (error) {
                        grError(`Failed to paste image: ${error}`);
                    }
                } else {
                    grInfo("Copied content is not a file");
                }
            }
        }
        if (!window.isSecureContext) {
            const cameraButton = container.querySelector('.source-selection > button:nth-of-type(2)');
            if (cameraButton) {
                cameraButton.style.display = "none";
            }
        }
        container.dataset.clipboardFixAttached = "true";
    });
}

onUiUpdate(fixClipboardPaste);


// copy image


async function copyImageToClipboard(img) {
    try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        ctx.drawImage(img, 0, 0);
        const imageName = getBasename(img.src);

        canvas.toBlob(async (blob) => {
            try {
                if (window.isSecureContext) {
                    await navigator.clipboard.write([
                        new ClipboardItem({
                            'image/png': blob,
                        }),
                    ]);
                }
                globalClipboardContent = new File([blob], imageName, { type: "image/png" });
            } catch (error) {
                console.error("Failed to copy image:", error);
                grError("Failed to copy image. See console for details.");
            }
        }, 'image/png');
    } catch (error) {
        console.error("Failed to process image:", error);
        grError("Failed to process image. See console for details.");
    }
}


// compare and copy buttons


function attachGalleryButton() {
    const galleryContainers = document.querySelectorAll('.gallery-container');
    const imageContainers = document.querySelectorAll('.image-container');
    const containers = [...galleryContainers, ...imageContainers];

    containers.forEach(container => {
        if (container.querySelector('.gallery-button')) return;
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
            copyButton.onclick = async () => {
                const img = container.querySelector("img");
                if (img) {
                    await copyImageToClipboard(img);
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
            compareButton.onclick = () => openComparePage();

            const toAButton = fullscreenButton.cloneNode(false);
            toAButton.textContent = "🡒A";
            toAButton.title = "Set as Image A";
            toAButton.classList.add("gallery-button");
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

onUiUpdate(attachGalleryButton);

