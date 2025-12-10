

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

    function connectToProgressSSE() {
        const eventSource = new EventSource('http://127.0.0.1:7860/mcww_api/progress_sse');
        const progressBar = document.getElementById('progressBar');
        const nodeProgressSegment = document.querySelector(".node-progress-segment");

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data) {
                progressContainer.style.display = "";
            } else {
                progressContainer.style.display = "none";
            }
            let {
                total_progress_max,
                total_progress_current,
                node_progress_max,
                node_progress_current
            } = data;


            if (node_progress_max !== null) {
                nodeProgressSegment.style.display = "block";
                const widthPercent = 100 / total_progress_max;
                nodeProgressSegment.style.width = `${widthPercent}%`;
                const leftPercent = widthPercent * total_progress_current;
                nodeProgressSegment.style.left = `${leftPercent}%`;

                total_progress_max *= node_progress_max;
                total_progress_current *= node_progress_max;
                total_progress_current += node_progress_current;
            } else {
                nodeProgressSegment.style.display = "none";
            }

            updateProgressContainerWidth();

            const totalProgressPercent = (total_progress_current / total_progress_max) * 100;
            progressBar.style.width = `${totalProgressPercent}%`;
        };

        eventSource.onerror = (error) => {
            console.error('Progress EventSource failed:', error);
            eventSource.close();
            setTimeout(connectToProgressSSE, 3000);
        };
    }

    // connectToProgressSSE();
});
