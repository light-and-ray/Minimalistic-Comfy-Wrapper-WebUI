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

            if (!data || data.total_progress_percent === null) {
                progressContainer.style.display = "none";
                progressBar.style.width = "0%";
                nodeProgressSegment.style.display = "none";
                TITLE.setProgress(null);
                return;
            }

            const {
                total_progress_percent,
                node_segment_width_percent,
                node_segment_left_percent,
                title_text
            } = data;

            progressBar.style.width = `${total_progress_percent}%`;

            if (node_segment_width_percent !== null) {
                nodeProgressSegment.style.display = "block";
                nodeProgressSegment.style.width = `${node_segment_width_percent}%`;
                nodeProgressSegment.style.left = `${node_segment_left_percent}%`;
            } else {
                // Node progress is not active
                nodeProgressSegment.style.display = "none";
            }
            TITLE.setProgress(title_text);
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