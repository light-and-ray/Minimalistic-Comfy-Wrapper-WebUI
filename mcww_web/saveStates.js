const AUTO_SAVE_STATE_MS = 15000;
const BUTTON_SELECTOR = '.save-states';
const MAX_WAIT_MS = 1000;
let saveStateInProgress = false;

function afterStatesSaved(...args) {
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

    if (webUIBrokenState) {
        console.warn(`[${new Date().toLocaleTimeString()}] Can't save in webui broken state...`);
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


let lastActiveTime = Date.now();
let isTabActive = true;

// Check tab visibility state
const handleVisibilityChange = () => {
    isTabActive = !document.hidden;
    if (isTabActive) {
        lastActiveTime = Date.now();
    }
};

// Modified save interval function
const saveInterval = () => {
    const now = Date.now();
    const inactiveDuration = now - lastActiveTime;

    // If tab is inactive and it's been less than AUTO_SAVE_STATE_MS since becoming inactive
    if (!isTabActive && inactiveDuration <= AUTO_SAVE_STATE_MS) {
        doSaveStates();
        // Schedule next execution 5x faster
        setTimeout(saveInterval, AUTO_SAVE_STATE_MS / 10);
    }
    // Normal interval
    else {
        doSaveStates();
        setTimeout(saveInterval, AUTO_SAVE_STATE_MS);
    }
};

// Initialize
document.addEventListener('visibilitychange', handleVisibilityChange);
saveInterval(); // Start the interval
