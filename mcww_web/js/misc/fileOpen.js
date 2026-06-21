
let g_hasHandledInitialLaunchQueue = false;

function _applySameWindowFileOpen() {
    document.querySelector(".file-open-buttons-new-window").classList.add("mcww-hidden");
    document.querySelector(".file-open-buttons-same-window").classList.remove("mcww-hidden");
}

function _applyNewWindowFileOpen() {
    document.querySelector(".file-open-buttons-new-window").classList.remove("mcww-hidden");
    document.querySelector(".file-open-buttons-same-window").classList.add("mcww-hidden");
}


if ("launchQueue" in window) {
    window.launchQueue.setConsumer(async (launchParams) => {
        const navigationEntries = performance.getEntriesByType("navigation");
        const isReload = navigationEntries.length > 0 && navigationEntries[0].type === "reload";
        const openedOnLoad = performance.now() < 3000;
        if (isReload && !g_hasHandledInitialLaunchQueue && openedOnLoad) {
            if (getSelectedMainUIPageFromUrl() == "fileOpen") {
                ensureProjectIsSelected();
            }
            return;
        }
        g_hasHandledInitialLaunchQueue = true;

        if (launchParams.files && launchParams.files.length) {
            const handledFile = launchParams.files[0];
            const blob = await handledFile.getFile();
            const url = createObjectURLWithAutoRevoke(blob);
            copyMediaToClipboard(url, handledFile.name);
            waitForElement(document, ".opened-file button.paste", (button) => {
                if (getSelectedMainUIPage() != "fileOpen") {
                    selectMainUIPage("fileOpen");
                }
                if (openedOnLoad) {
                    _applyNewWindowFileOpen();
                } else {
                    _applySameWindowFileOpen();
                }
                button.click();
            });
        } else if (!openedOnLoad && launchParams.targetURL) {
            const targetURLPage = new URL(launchParams.targetURL).searchParams.get("page_") ?? "project";
            const newWindow = window.open(getUrlForNewPage(targetURLPage), '_blank', 'popup=yes');
            if (!newWindow || newWindow.closed) {
                grError("Allow popups to open a new window via shortcuts");
            }
        }
    });
}


function afterFileOpened() {
    const fileStem = document.querySelector(".opened-file .filename .stem")?.textContent;
    const fileExt = document.querySelector(".opened-file .filename .ext")?.textContent;
    let fileName = null;
    if (fileStem && fileExt) {
        fileName = fileStem + fileExt;
    }
    TITLE.setOpenedFileName(fileName);
    if (fileName) {
        waitForElement(document, ".opened-file .download-link", (link) => {
            if (isImageUrl(link.href) || isVideoUrl(link.href) || isAudioUrl(link.href)) {
                copyMediaToClipboard(link.href);
                topRightAlert("Opened file has been copied into clipboard");
            }
        });
    }
}


function _openFileOpenPageSameWindow() {
    if (getSelectedMainUIPage() !== "fileOpen") {
        selectMainUIPage("fileOpen");
    }
    waitForElement(document, ".opened-file button.paste", (button) => {
        _applySameWindowFileOpen();
        button.click();
    });
}


document.addEventListener('drop', (event) => {
    event.preventDefault();
    const files = [...event.dataTransfer.items]
    .map((item) => item.getAsFile())
    .filter((file) => file);
    if (files.length > 1) {
        grError("Only 1 file drop is supported");
    }
    if (files.length === 1) {
        const file = files[0];
        const blob = new Blob([file], { type: file.type });
        const url = createObjectURLWithAutoRevoke(blob);
        copyMediaToClipboard(url, file.name);
        _openFileOpenPageSameWindow();
    }
});


async function openFileFromSystemClipboard() {
    try {
        const clipboardItems = await navigator.clipboard.read();
        for (const clipboardItem of clipboardItems) {
            for (const type of clipboardItem.types) {
                if (type.startsWith('image/') || type.startsWith('video/')) {
                    const blob = await clipboardItem.getType(type);
                    const blobUrl = createObjectURLWithAutoRevoke(blob);
                    copyMediaToClipboard(blobUrl, null);
                    _openFileOpenPageSameWindow();
                    return;
                }
            }
        }
        topRightAlert("File is not found in the system clipboard", 2000);
    } catch (error) {
        grError("Failed to read system clipboard");
        console.error("Failed to read system clipboard:", error);
    }
}


async function openFileFromPasteEvent(event) {
    const clipboardItems = (event.clipboardData || event.originalEvent.clipboardData).items;
    for (const clipboardItem of clipboardItems) {
        const type = clipboardItem.type;
        if (type.startsWith('image/') || type.startsWith('video/')) {
            const file = clipboardItem.getAsFile();
            if (file) {
                const blobUrl = createObjectURLWithAutoRevoke(file);
                copyMediaToClipboard(blobUrl, null);
                _openFileOpenPageSameWindow();
            }
        }
    }
}

