const AUTO_SAVE_STATE_MS = 15000;
const BUTTON_SELECTOR = '.save_states';
const MAX_WAIT_MS = 1000;
let saveStateInProgress = false;

function afterStateSaved(...args) {
    saveStateInProgress = false;
}

async function waitForSave() {
    const startTime = Date.now();
    while (saveStateInProgress && (Date.now() - startTime < MAX_WAIT_MS)) {
        await new Promise(resolve => setTimeout(resolve, 10));
    }
    if (saveStateInProgress) {
        console.warn(`[${new Date().toLocaleTimeString()}] Save operation timed out`);
        saveStateInProgress = false;
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
            await waitForSave();
        } catch (error) {
            console.error(`[${new Date().toLocaleTimeString()}] Error clicking the button:`, error);
            saveStateInProgress = false;
        }
    }
}

const intervalId = setInterval(doSaveStates, AUTO_SAVE_STATE_MS);

