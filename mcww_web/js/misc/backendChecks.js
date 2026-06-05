
const originalFetch = window.fetch;
const BACKEND_CHECK_INTERVAL = 2500;
const BACKEND_NOT_AVAILABLE_BROKEN_STATE_TIMEOUT = 60000;
let g_backendNotAvailableInARow = 0;
let g_inBrokenState = false;
let g_restartIsExpected = false;
let g_restartIsExpectedTimeout = null;

function setRestartIsExpected() {
    g_restartIsExpected = true;
    if (g_restartIsExpectedTimeout) {
        clearTimeout(g_restartIsExpectedTimeout);
    }
    g_restartIsExpectedTimeout = setTimeout(() => {
        g_restartIsExpected = false;
    }, 60000);
}

function cancelRestartIsExpected() {
    g_restartIsExpected = false;
    if (g_restartIsExpectedTimeout) {
        clearTimeout(g_restartIsExpectedTimeout);
    }
}


async function checkSameAppIdOnUiLoaded() {
    try {
        const response = await originalFetch('/config');
        if (!response.ok) {
            return;
        }
        const config = await response.json();
        if (window.gradio_config.app_id !== config.app_id) {
            reloadPage();
        }
    } catch (error) {
        return;
    }
}


async function connectionTest() {
    try {
        const response = await originalFetch('/config');
        if (response && response.ok) {
            return await response.json();;
        }
    } catch (error) {
        // nothing
    }
    return null;
}


function setBrokenState() {
    window.fetch = () => {
        throw new Error("All connections are blocked due to broken state");
    };
    g_inBrokenState = true;
}


function setErrorState(errorText) {
    if (OPTIONS.autoRefreshPageOnBackendRestarted) {
        reloadPage();
    }
    grError(errorText);
    setInterval(() => {
        grError(errorText);
    }, 10000);
    setBrokenState();
}


async function backendCheck(fromUiLoaded=false) {
    try {
        const connectionTestResponse = await connectionTest();
        if (connectionTestResponse) {
            g_backendNotAvailableInARow = 0;
            document.querySelector("#noConnection").classList.add("mcww-hidden");
            const config = connectionTestResponse;
            if (window.gradio_config.app_id !== config.app_id) {
                setErrorState("Backend restarted, please <a href=''>reload the page</a>");
            }
        } else {
            g_backendNotAvailableInARow += 1;
            if (fromUiLoaded) {
                setBrokenState();
                showOfflinePlaceholder();
                const testInterval = async () => {
                    if (await connectionTest()) {
                        if (OPTIONS.autoRefreshPageOnBackendRestarted) {
                            reloadPage();
                        }
                        const message = "Connection is available, please <a href=''>reload the page</a>";
                        grInfo(message);
                        setTimeout(testInterval, 10000);
                    } else {
                        setTimeout(testInterval, 1000);
                    }
                };
                testInterval();
            } else {
                // if (g_backendNotAvailableInARow*BACKEND_CHECK_INTERVAL > BACKEND_NOT_AVAILABLE_BROKEN_STATE_TIMEOUT) {
                //     setErrorState("The backend has been unavailable for too long, please <a href=''>reload the page</a>");
                // } else {
                // }
                if (g_isTabActive) {
                    document.querySelector("#noConnection").classList.remove("mcww-hidden");
                }
            }
        }
    } catch (error) {
        console.log(error);
        grError("Error on backend check");
    } finally {
        if (!g_inBrokenState) {
            setTimeout(backendCheck, BACKEND_CHECK_INTERVAL);
        }
    }
}

onUiLoaded(() => {
    const noConnection = document.createElement('div');
    noConnection.id = "noConnection";
    noConnection.innerHTML = MCWW.SVG["noConnection"];
    noConnection.classList.add("mcww-hidden");
    document.querySelector("main").appendChild(noConnection);
    backendCheck(true);
});

function onGradioAppBroken() {
    if (!g_inBrokenState && !g_restartIsExpected) {
        setErrorState("Connection to the server was lost, please <a href=''>reload the page</a>");
    }
    if (g_restartIsExpected) {
        grInfo("Restarting...");
    }
}

