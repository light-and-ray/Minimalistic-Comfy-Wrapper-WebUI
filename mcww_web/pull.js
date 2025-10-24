const PULL_INTERVAL_TIME = 100;

const doPull = async () => {
    const button = document.querySelector('.mcww-pull');
    if (button) {
        // Extract pullData from the button's content
        const pullData = JSON.parse(button.textContent || button.innerText);

        if (pullData.type === "queue") {
            try {
                // Fetch the current version from the API
                const response = await fetch('/mcww_api/queue_version');
                const currentVersion = await response.text(); // Read as plain text (integer)
                const currentVersionInt = parseInt(currentVersion, 10); // Convert to integer
                // Compare versions
                if (pullData.oldVersion !== currentVersionInt) {
                    button.click();
                }
            } catch (error) {
                console.error("Error fetching queue version:", error);
            }
        }
    }
};

setInterval(doPull, PULL_INTERVAL_TIME);
