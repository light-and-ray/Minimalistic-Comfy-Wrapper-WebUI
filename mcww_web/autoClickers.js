

(function() { // '.save_states' autoclick
    // Define the time interval in milliseconds (3 seconds)
    const CLICK_INTERVAL_MS = 3000;
    const BUTTON_SELECTOR = '.save_states';

    /**
     * Finds the target button and performs a click action on it.
     * Logs status messages to the console.
     */
    function clickSaveStatesButton() {
        // 1. Find the button using its class selector
        const targetButton = document.querySelector(BUTTON_SELECTOR);

        if (targetButton) {
            // 2. Button found. Attempt to click it.
            try {
                // Programmatically trigger the click event
                targetButton.click();
                console.log(`[${new Date().toLocaleTimeString()}] Successfully clicked the button with class '${BUTTON_SELECTOR}'`);
            } catch (error) {
                console.error(`[${new Date().toLocaleTimeString()}] Error clicking the button:`, error);
            }
        } else {
            // 3. Button not found. Log a message.
            console.log(`[${new Date().toLocaleTimeString()}] Button with class '${BUTTON_SELECTOR}' not found on the page.`);
            // Optionally, you could use clearInterval here to stop trying if the button is permanently missing.
        }
    }

    // Start the interval timer. It calls the function every 3000 milliseconds.
    console.log(`Starting auto-clicker. Will attempt to click '${BUTTON_SELECTOR}' every ${CLICK_INTERVAL_MS / 1000} seconds.`);

    const intervalId = setInterval(clickSaveStatesButton, CLICK_INTERVAL_MS);
})();
