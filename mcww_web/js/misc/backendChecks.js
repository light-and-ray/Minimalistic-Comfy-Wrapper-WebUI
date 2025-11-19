
var webUIBrokenState = false;

async function ensureSameAppId() {
    try {
        if (webUIBrokenState) {
            return;
        }
        const response = await fetch('/config');
        if (!response.ok) {
            grWarning("Backend is not available");
            return;
        }

        const config = await response.json();

        if (window.gradio_config.app_id !== config.app_id) {
            if (!window.gradio_config.app_id) { // null on mobile browser after partial unloading
                grError(`JS: window.gradio_config.app_id = ${window.gradio_config.app_id}`);
            }
            const errorText = "Backend restarted, please <a href=''>reload the page</a>";
            grError(errorText);
            setInterval(() => {
                grError(errorText);
            }, 10000);
            webUIBrokenState = true;
            window.fetch = () => {
                throw new Error("All connections are blocked due to broken state");
            };
        }
    } catch (error) {
        grWarning("Backend is not available");
    }
}
setInterval(ensureSameAppId, 5100);

