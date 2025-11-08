
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


var globalCompareImageA = null;
var globalCompareImageB = null;

function swapGlobalImagesAB() {
    const oldA = globalCompareImageA;
    globalCompareImageA = globalCompareImageB;
    globalCompareImageB = oldA;
}

function openComparePage() {
    selectMainUIPage("compare");
    waitForElement("#compareImageA_url textarea", (textareaA) => {
        waitForElement("#compareImageB_url textarea", (textareaB) => {
            if (globalCompareImageA) {
                textareaA.value = globalCompareImageA;
                textareaA.dispatchEvent(new Event('input', { bubbles: true }));
            }
            if (globalCompareImageB) {
                textareaB.value = globalCompareImageB;
                textareaB.dispatchEvent(new Event('input', { bubbles: true }));
            }
            button = document.querySelector("#compareImagesButton");
            button.click();
        });
    });
}


function attachCompareButton() {
    const galleryContainers = document.querySelectorAll('.gallery-container');
    const imageContainers = document.querySelectorAll('.image-container');
    const containers = [...galleryContainers, ...imageContainers];

    containers.forEach(container => {
        if (container.parentElement.classList.contains("no-compare")) return;
        if (container.querySelector('button[title="Compare"]')) return;

        const fullscreenButton = container.querySelector('button[title="Fullscreen"]');
        if (!fullscreenButton) return;

        // Copy classes and styles from the fullscreen button
        const compareButton = fullscreenButton.cloneNode(false);
        compareButton.textContent = "A|B";
        compareButton.title = "Compare";
        compareButton.onclick = () => openComparePage();

        const toAButton = fullscreenButton.cloneNode(false);
        toAButton.textContent = "🡒A";
        toAButton.title = "Set as Image A";
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
        toBButton.onclick = () => {
            const img = container.querySelector("img");
            if (img) {
                globalCompareImageB = img.src;
                mouseAlert("Image set as Image B");
            }
        };

        const copyButton = fullscreenButton.cloneNode(false);
        copyButton.textContent = "⎘";
        copyButton.title = "Copy to Clipboard";
        copyButton.onclick = async () => {
            const img = container.querySelector("img");
            if (img) {
                await copyImageToClipboard(img);
                mouseAlert("Image copied to clipboard");
            }
        };

        const firstSibling = fullscreenButton.parentNode.childNodes[0];
        fullscreenButton.parentNode.insertBefore(copyButton, firstSibling);
        fullscreenButton.parentNode.insertBefore(compareButton, firstSibling);
        fullscreenButton.parentNode.insertBefore(toAButton, firstSibling);
        fullscreenButton.parentNode.insertBefore(toBButton, firstSibling);
    });
}

onUiUpdate(attachCompareButton);


///////    mouse alert


function mouseAlert(message, duration = 350) {
    const alertElement = document.createElement('div');
    alertElement.className = 'mouse-alert';
    alertElement.textContent = message;

    const progressBar = document.createElement('div');
    progressBar.className = 'mouse-alert-progress';
    alertElement.appendChild(progressBar);

    const positionAtCursor = (e) => {
        const x = e ? e.clientX : window.innerWidth / 2;
        const y = e ? e.clientY + 57 : window.innerHeight / 2;
        alertElement.style.left = `${x}px`;
        alertElement.style.top = `${y}px`;
    };

    document.body.appendChild(alertElement);

    // Animate progress bar
    progressBar.style.transitionDuration = `${duration}ms`;
    setTimeout(() => {
        progressBar.style.transform = 'scaleX(0)';
    }, 10);

    setTimeout(() => {
        alertElement.remove();
    }, duration);

    const lastMouseEvent = window.lastMouseEvent || { clientX: window.innerWidth / 2, clientY: window.innerHeight / 2 };
    positionAtCursor(lastMouseEvent);
}

document.addEventListener('mousemove', (e) => {
    window.lastMouseEvent = e;
});

