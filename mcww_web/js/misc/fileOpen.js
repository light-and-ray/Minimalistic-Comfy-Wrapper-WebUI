
if ("launchQueue" in window) {
    window.launchQueue.setConsumer(async (launchParams) => {
        if (getSessionStorageVariable("fileOpenHandled")) {
            if (getSelectedMainUIPageFromUrl() == "fileOpen") {
                ensureProjectIsSelected();
            }
            return;
        }
        if (launchParams.files && launchParams.files.length) {
            try {
                window.resizeTo(800, 600);
            } catch (error) {
                console.log(error);
            }
            const handledFile = launchParams.files[0];
            const blob = await handledFile.getFile();
            const url = window.URL.createObjectURL(blob);
            copyMediaToClipboard(url, handledFile.name);
            waitForElement(document, ".opened-file button.paste", (button) => {
                document.querySelector(".file-open-buttons-new-window").classList.remove("mcww-hidden");
                document.querySelector(".file-open-buttons-same-window").classList.add("mcww-hidden");
                button.click();
                setSessionStorageVariable("fileOpenHandled", true);
            });
        } else {
            if (getSelectedMainUIPageFromUrl() == "fileOpen") {
                ensureProjectIsSelected();
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
            if (!isModel3DUrl(link.href)) {
                copyMediaToClipboard(link.href);
                grInfo("Opened file has been copied into clipboard");
            }
        });
    }
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
        if (getSelectedMainUIPage() !== "fileOpen") {
            selectMainUIPage("fileOpen");
        }
        const file = files[0];
        const blob = new Blob([file], { type: file.type });
        const url = window.URL.createObjectURL(blob);
        copyMediaToClipboard(url, file.name);
        waitForElement(document, ".opened-file button.paste", (button) => {
            document.querySelector(".file-open-buttons-new-window").classList.add("mcww-hidden");
            document.querySelector(".file-open-buttons-same-window").classList.remove("mcww-hidden");
            button.click();
        });
    }
});
