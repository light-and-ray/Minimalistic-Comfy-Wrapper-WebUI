
if ("launchQueue" in window) {
    window.launchQueue.setConsumer(async (launchParams) => {
        if (launchParams.files && launchParams.files.length) {
            const handledFile = launchParams.files[0];
            const blob = await handledFile.getFile();
            const url = window.URL.createObjectURL(blob);
            copyImageToClipboard(url);
            waitForElement(".opened-image button.paste", (button) => {
                grInfo("Opened image has been copied into clipboard");
                button.click();
            });
        }
    });
}
