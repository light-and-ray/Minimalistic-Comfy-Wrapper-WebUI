
if ("launchQueue" in window) {
    window.launchQueue.setConsumer(async (launchParams) => {
        if (getSessionStorageVariable("fileOpenHandled")) {
            if (getSelectedMainUIPageFromUrl() == "fileOpen") {
                ensureProjectIsSelected();
            }
            return;
        }
        if (launchParams.files && launchParams.files.length) {
            const handledFile = launchParams.files[0];
            const blob = await handledFile.getFile();
            const url = window.URL.createObjectURL(blob);
            copyMediaToClipboard(url);
            waitForElement(".opened-file button.paste", (button) => {
                button.click();
                waitForElement(".opened-file .download-link", (link) => {
                    copyMediaToClipboard(link.href);
                    grInfo("Opened file has been copied into clipboard");
                });
                setSessionStorageVariable("fileOpenHandled", true);
            });
        } else {
            if (getSelectedMainUIPageFromUrl() == "fileOpen") {
                ensureProjectIsSelected();
            }
        }
    });
}
