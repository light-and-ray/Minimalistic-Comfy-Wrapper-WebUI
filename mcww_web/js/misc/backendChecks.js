
async function checkSameAppIdOnUiLoaded() {
    try {
        if (webUIBrokenState) {
            reloadPage();
        }
        const response = await fetch('/config');
        if (!response.ok) {
            reloadPage();
        }
        const config = await response.json();
        if (window.gradio_config.app_id !== config.app_id) {
            reloadPage();
        }
    } catch (error) {
        reloadPage();
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
            response = await fetch('/config', { signal: AbortSignal.timeout(1000) });
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
                if (executedOnLoaded) {
                    grWarning("Backend is not available");
                } else {
                    setBrokenState();
                    showOfflinePlaceholder();
                }
            }
        }
    } catch (error) {
        console.log(error);
        grError("Error on backend check");
    }
}
setInterval(backendCheck, 5100);
setTimeout(backendCheck, 200);

