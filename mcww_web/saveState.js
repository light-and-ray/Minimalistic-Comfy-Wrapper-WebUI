const AUTO_SAVE_STATE_MS = 15000;
const BUTTON_SELECTOR = '.save_states';
const MAX_WAIT_MS = 1000;
let saveStateInProgress = false;

async function waitForSave() {
    const startTime = Date.now();
    while (saveStateInProgress && (Date.now() - startTime < MAX_WAIT_MS)) {
        await new Promise(resolve => setTimeout(resolve, 10));
    }
}

async function doSaveStates(...args) {
    if (saveStateInProgress) {
        console.warn(`[${new Date().toLocaleTimeString()}] Save already in progress, skipping...`);
        await waitForSave();
        return;
    }

    const saveStatesButton = document.querySelector(BUTTON_SELECTOR);
    if (saveStatesButton) {
        saveStateInProgress = true;
        try {
            // console.log(`[${new Date().toLocaleTimeString()}] Clicking save button...`);
            saveStatesButton.click();

            // Wait until saveStateInProgress is set to false, but with timeout
            await waitForSave();

            if (saveStateInProgress) {
                console.warn(`[${new Date().toLocaleTimeString()}] Save operation timed out`);
                saveStateInProgress = false; // Force reset if timed out
            } else {
                // console.log(`[${new Date().toLocaleTimeString()}] Save completed, ready for next interval`);
            }
        } catch (error) {
            console.error(`[${new Date().toLocaleTimeString()}] Error clicking the button:`, error);
            saveStateInProgress = false; // Reset in case of error
        }
    }
}

const intervalId = setInterval(doSaveStates, AUTO_SAVE_STATE_MS);

function afterStateSaved(...args) {
    saveStateInProgress = false;
}
