
function openPresetsPage() {
    selectMainUIPage("presets");
}


onPageSelected((page) => {
    if (page === "presets") {
        waitForElement('.refresh-presets', (button) => {
            button.click();
            waitForElement(".after-presets-edited", (button) => {
                button.click();
            })
        })
    }
});


function hidePresetsEditorArrows() {
    const row = document.querySelector('.presets-arrows-row');
    if (row) {
        row.style.display = "none";
    }
}
