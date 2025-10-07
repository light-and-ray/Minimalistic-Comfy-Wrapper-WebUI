
(function() {
    const CLICK_INTERVAL_MS = 15000;
    const BUTTON_SELECTOR = '.save_states';

    function clickSaveStatesButton() {
        const targetButton = document.querySelector(BUTTON_SELECTOR);

        if (targetButton) {
            try {
                targetButton.click();
            } catch (error) {
                console.error(`[${new Date().toLocaleTimeString()}] Error clicking the button:`, error);
            }
        }
    }

    const intervalId = setInterval(clickSaveStatesButton, CLICK_INTERVAL_MS);
})();
