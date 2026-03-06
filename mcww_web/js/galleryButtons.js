
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
                    await dropMediaFromClipboard(dropButton);
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
            pasteButton.innerHTML = PASTE_SVG;
            pasteButton.title = "Paste from clipboard";
            pasteButton.onclick = async () => {
                try {
                    mouseAlert("Pasting...");
                    const dropButton = uploadToolButton.querySelector('button:has(>input)');
                    await dropMediaFromClipboard(dropButton);
                } catch (error) {
                    const text = `Failed to paste image: ${error}`;
                    console.error(text);
                    grError(text);
                }
            };
            uploadToolButton.parentNode.insertBefore(pasteButton, uploadToolButton);
        }
    });

    const uploadGalleries = updatedElements.querySelectorAll('.upload-gallery:not(:has(button.paste)), ' +
            '.video-container>.upload-container:not(:has(button.paste)), ' +
            '.audio-container:not(:has(button.paste))'
    );
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
                    await dropMediaFromClipboard(uploadButton);
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
    const containers = updatedElements.querySelectorAll('.gallery-container, .image-container, .video-container, .audio-container, .mcww-other-gallery');
    containers.forEach(container => {
        if (container.querySelector('.gallery-button')) return;
        if (!container.parentElement) return;
        let needCompare = true;
        let needCopy = true;
        let needOpen = true;

        if (container.parentElement.classList.contains("no-compare") || container.classList.contains("no-compare")) {
            needCompare = false;
        }
        if (container.parentElement.classList.contains("no-copy") || container.classList.contains("no-copy")) {
            needCopy = false;
        }
        if (container.parentElement.classList.contains("no-open") || container.classList.contains("no-open")) {
            needOpen = false;
        }

        const referenceButton = container.querySelector('button.icon-button:not([disabled])');
        if (!referenceButton) return;
        const wrapper = container.querySelector('.icon-button-wrapper');
        const firstSibling = wrapper.childNodes[0];

        if (needCopy) {
            const copyButton = referenceButton.cloneNode(false);
            copyButton.textContent = "⎘";
            copyButton.title = "Copy to Clipboard";
            copyButton.classList.add("gallery-button");
            copyButton.classList.add("copy");
            copyButton.onclick = () => {
                const media = container.querySelector("img, video, .download-link");
                if (media) {
                    copyMediaToClipboard(media);
                    mouseAlert("Copied to clipboard");
                }
            };
            wrapper.insertBefore(copyButton, firstSibling);
        }

        if (needOpen) {
            const openButton = referenceButton.cloneNode(false);
            openButton.textContent = "🡕";
            openButton.title = "Open in New Window";
            openButton.classList.add("gallery-button", "force-text-style");
            openButton.classList.add("open");
            openButton.onclick = () => {
                const media = container.querySelector("img, video, .download-link");
                const link = media?.src || media?.href;
                if (link) {
                    window.open(link, '_blank', 'popup=yes');
                }
            };
            wrapper.insertBefore(openButton, firstSibling);

            if ('pictureInPictureEnabled' in document && container.querySelector('video')) {
                const PiPSvg = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 20 24" fill="none"
                            stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="2" y="6" width="16" height="12" rx="1" />
                        <rect x="11" y="12" width="5" height="4" rx="0.5" />
                    </svg>
                    `;
                const pipButton = referenceButton.cloneNode(false);
                pipButton.innerHTML = PiPSvg;
                pipButton.title = "Picture in Picture";
                pipButton.classList.add("gallery-button");
                pipButton.classList.add("pip");
                pipButton.onclick = async () => {
                    if (document.pictureInPictureElement) {
                        await document.exitPictureInPicture();
                    }
                    video = container.querySelector('video');
                    await video?.requestPictureInPicture();
                }
                wrapper.insertBefore(pipButton, firstSibling);
            }
        }

        if (needCompare) {
            const compareButton = referenceButton.cloneNode(false);
            compareButton.textContent = "A|B";
            compareButton.title = "Compare";
            compareButton.classList.add("gallery-button");
            compareButton.classList.add("compare");
            compareButton.onclick = () => openComparePage();

            const toAButton = referenceButton.cloneNode(false);
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

            const toBButton = referenceButton.cloneNode(false);
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

            wrapper.insertBefore(compareButton, firstSibling);
            wrapper.insertBefore(toAButton, firstSibling);
            wrapper.insertBefore(toBButton, firstSibling);
        }
    });
}

onUiUpdate(attachGalleryButtons);

