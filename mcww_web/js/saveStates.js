const AUTO_SAVE_STATE_MS = 15000;
const AUTO_SAVE_BUTTON_SELECTOR = '.save-states';
const AUTO_SAVE_MAX_WAIT_MS = 2000;
let saveStateInProgress = false;

function afterStatesSaved() {
    saveStateInProgress = false;
}

async function waitForSave() {
    const startTime = Date.now();
    while (saveStateInProgress && (Date.now() - startTime < AUTO_SAVE_MAX_WAIT_MS)) {
        await sleep(100);
    }
    if (saveStateInProgress) {
        console.warn(`[${new Date().toLocaleTimeString()}] Save operation timed out`);
        // grWarning("Save webUi state operation timed out");
        saveStateInProgress = false;
    }
}

async function doSaveStates() {
    if (saveStateInProgress) {
        console.warn(`[${new Date().toLocaleTimeString()}] Save already in progress, skipping...`);
        await waitForSave();
        return;
    }

    if (webUIBrokenState) {
        console.warn(`[${new Date().toLocaleTimeString()}] Can't save in webui broken state...`);
        return;
    }

    const saveStatesButton = document.querySelector(AUTO_SAVE_BUTTON_SELECTOR);
    if (saveStatesButton) {
        saveStateInProgress = true;
        try {
            saveStatesButton.click();
            await waitForSave();
        } catch (error) {
            console.error(`[${new Date().toLocaleTimeString()}] Error clicking the button:`, error);
            saveStateInProgress = false;
        }
    }
}


const saveInterval = () => {
    const now = Date.now();
    const inactiveDuration = now - g_lastActiveTime;

    if (!g_isTabActive && inactiveDuration <= AUTO_SAVE_STATE_MS) {
        doSaveStates();
        setTimeout(saveInterval, AUTO_SAVE_STATE_MS / 10);
    }
    else {
        doSaveStates();
        setTimeout(saveInterval, AUTO_SAVE_STATE_MS);
    }
};

saveInterval();
