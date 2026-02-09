const PULL_INTERVAL_TIME = 100;
const PULL_MAX_WAIT_MS = 3000;
const SLEEP_BETWEEN_PULLS = 800;


let pullInProgress = false;

function pullIsDone() {
    pullInProgress = false;
    selectFirstEntryInPseudoGalleries();
}

async function waitForPull() {
    const startTime = Date.now();
    while (pullInProgress && (Date.now() - startTime < PULL_MAX_WAIT_MS)) {
        await sleep(100);
    }
    if (pullInProgress) {
        console.warn(`[${new Date().toLocaleTimeString()}] Pull operation timed out`);
        // grWarning("Pull operation timed out");
        pullInProgress = false;
    }
}

const doPull = async () => {
    try {
        const button = document.querySelector('.mcww-pull');
        if (button && g_isTabActive) {
            const pullData = JSON.parse(button.textContent || button.innerText);

            if (pullData.type === "queue") {
                try {
                    const response = await fetch('/mcww_api/queue_version');
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const currentVersion = await response.text();
                    const currentVersionInt = parseInt(currentVersion, 10);

                    if (pullData.oldVersion !== currentVersionInt) {
                        pullInProgress = true;
                        button.click();
                        await waitForPull();
                        pullData.oldVersion = currentVersionInt;
                        button.textContent = JSON.stringify(pullData);
                        await sleep(SLEEP_BETWEEN_PULLS);
                    }
                } catch (error) {
                    console.error("Error fetching queue version:", error);
                }
            }
            else if (pullData.type === "outputs") {
                try {
                    const response = await fetch('/mcww_api/outputs_version/' + pullData.outputs_key);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const currentVersion = await response.text();
                    const currentVersionInt = parseInt(currentVersion, 10);

                    if (pullData.oldVersion !== currentVersionInt) {
                        pullInProgress = true;
                        button.click();
                        await waitForPull();
                        pullData.oldVersion = currentVersionInt;
                        button.textContent = JSON.stringify(pullData);
                        await sleep(SLEEP_BETWEEN_PULLS);
                    }
                } catch (error) {
                    console.error("Error fetching outputs version:", error);
                }
            }
        }
    } catch (error) {
        console.error("Error in doPull:", error);
    } finally {
        setTimeout(doPull, PULL_INTERVAL_TIME);
    }

};

onUiLoaded(doPull);
