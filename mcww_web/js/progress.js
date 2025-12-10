

onUiLoaded(() => {
    const sidebarParent = document.querySelector('.sidebar-parent');
    const progressContainer = document.querySelector('.progress-container');
    function updateProgressContainerWidth() {
        const width = getContentWidth(sidebarParent);
        if (width) {
            progressContainer.style.width = `${width}px`;
        }
    }
    window.addEventListener('resize', updateProgressContainerWidth);
    window.updateProgressContainerWidth = updateProgressContainerWidth;

    function connectToProgressSSE() {
        const eventSource = new EventSource('/mcww_api/progress_sse');
        const progressBar = document.getElementById('progressBar');
        const nodeProgressSegment = document.querySelector(".node-progress-segment");

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateProgressContainerWidth();

            if (!data) {
                progressContainer.style.display = "none";
                progressBar.style.width = "0%";
                nodeProgressSegment.style.display = "none";
                TITLE.setProgress(null);
                return;
            }
            let {
                total_progress_max,
                total_progress_current,
                node_progress_max,
                node_progress_current
            } = data;

            total_progress_current = Math.min(total_progress_current, total_progress_max);

            if (node_progress_max !== null) {
                nodeProgressSegment.style.display = "block";
                const widthPercent = 100 / total_progress_max;
                nodeProgressSegment.style.width = `${widthPercent}%`;
                const leftPercent = widthPercent * total_progress_current;
                nodeProgressSegment.style.left = `${leftPercent}%`;
                const totalProgressPercentTitle = total_progress_current / total_progress_max * 100;
                const nodeProgressPercentTitle = node_progress_current / node_progress_max * 100;
                TITLE.setProgress(`[${Math.round(totalProgressPercentTitle)}%] [${Math.round(nodeProgressPercentTitle)}%]`)

                total_progress_max *= node_progress_max;
                total_progress_current *= node_progress_max;
                total_progress_current += node_progress_current;
            } else {
                nodeProgressSegment.style.display = "none";
                const totalProgressPercentTitle = total_progress_current / total_progress_max * 100;
                TITLE.setProgress(`[${Math.round(totalProgressPercentTitle)}%]`)
            }

            const totalProgressPercent = (total_progress_current / total_progress_max) * 100;
            progressBar.style.width = `${totalProgressPercent}%`;
            progressContainer.style.display = "";
        };

        eventSource.onerror = (error) => {
            console.error('Progress EventSource failed:', error);
            eventSource.close();
            setTimeout(connectToProgressSSE, 3000);
        };
    }

    connectToProgressSSE();
});
