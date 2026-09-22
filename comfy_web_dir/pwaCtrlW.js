function isRunningInPWA() {
    return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
}

document.addEventListener('keydown', function(event) {
    if (!isRunningInPWA()) {
        return;
    }
    if ((event.ctrlKey || event.metaKey) && event.code ==='KeyW') {
        const closeTabButton = document.querySelector('.workflow-tabs-container .p-togglebutton.p-togglebutton-checked button.close-button');
        if (closeTabButton) {
            event.preventDefault();
            closeTabButton.click();
        }
    }
});
