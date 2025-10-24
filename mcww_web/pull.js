const PULL_INTERVAL_TIME = 100;

const doPull = async () => {
    try {
        const button = document.querySelector('.mcww-pull');
        if (button) {
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
                        button.click();
                        console.log("!!! queue clicked");

                        pullData.oldVersion = currentVersionInt;
                        button.textContent = JSON.stringify(pullData);
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
                        button.click();
                        console.log("!!! outputs clicked");
                        pullData.oldVersion = currentVersionInt;
                        button.textContent = JSON.stringify(pullData);
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

setTimeout(doPull, PULL_INTERVAL_TIME);