
const BACKEND_CHECK_INTERVAL = 5100;

async function checkSameAppIdOnUiLoaded() {
    try {
        const response = await fetch('/config');
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
    let response = null;
    try {
        response = await fetch('/config');
        if (!response.ok) {
            response = null;
        }
    } catch (error) {
        // nothing
    }
    return response;
}


async function backendCheck() {
    let needLoop = true;
    try {
        const connectionTestResponse = await connectionTest();
        if (connectionTestResponse) {
            const config = await connectionTestResponse.json();
            if (window.gradio_config.app_id !== config.app_id) {
                const errorText = "Backend restarted, please <a href=''>reload the page</a>";
                grError(errorText);
                setInterval(() => {
                    grError(errorText);
                }, 10000);
                needLoop = false;
                window.fetch = () => {
                    throw new Error("All connections are blocked due to broken state");
                };
            }
        } else {
            if (uiElementIsVisible(document.querySelector(".init-ui"))) {
                showOfflinePlaceholder();
                needLoop = false;
                const testInterval = setInterval(async () => {
                    if (await connectionTest()) {
                        clearInterval(testInterval);
                        const message = "Connection is available, please <a href=''>reload the page</a>";
                        setInterval(() => {
                            grInfo(message);
                        }, 10000);
                    }
                }, 1000);
            } else {
                grWarning("Backend is not available");
            }
        }
    } catch (error) {
        console.log(error);
        grError("Error on backend check");
    } finally {
        if (needLoop) {
            setTimeout(backendCheck, BACKEND_CHECK_INTERVAL);
        }
    }
}

onUiLoaded(backendCheck);

