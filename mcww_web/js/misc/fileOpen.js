
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
                grInfo("Opened file has been copied into clipboard");
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
