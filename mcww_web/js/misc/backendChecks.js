
const BACKEND_CHECK_INTERVAL = 5100;
const BACKEND_CHECK_TIMEOUT = 2000;

async function checkSameAppIdOnUiLoaded() {
    try {
        if (webUIBrokenState) {
            return;
        }
        const response = await fetch('/config', { signal: AbortSignal.timeout(BACKEND_CHECK_TIMEOUT) });
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


var webUIBrokenState = false;

function setBrokenState() {
    webUIBrokenState = true;
    window.fetch = () => {
        throw new Error("All connections are blocked due to broken state");
    };
}


async function backendCheck() {
    try {
        let isAvailable = true;
        let response = null;
        try {
            response = await fetch('/config', { signal: AbortSignal.timeout(BACKEND_CHECK_TIMEOUT) });
            if (!response.ok) {
                isAvailable = false;
            }
        } catch (error) {
            isAvailable = false;
        }

        if (!webUIBrokenState) {
            if (isAvailable) {
                const config = await response.json();
                if (window.gradio_config.app_id !== config.app_id) {
                    const errorText = "Backend restarted, please <a href=''>reload the page</a>";
                    grError(errorText);
                    setInterval(() => {
                        grError(errorText);
                    }, 10000);
                    setBrokenState();
                }
            } else {
                if (uiElementIsVisible(document.querySelector(".init-ui"))) {
                    setBrokenState();
                    showOfflinePlaceholder();
                } else {
                    grWarning("Backend is not available");
                }
            }
        }
    } catch (error) {
        console.log(error);
        grError("Error on backend check");
    } finally {
        setTimeout(backendCheck, BACKEND_CHECK_INTERVAL);
    }
}

onUiLoaded(backendCheck);

