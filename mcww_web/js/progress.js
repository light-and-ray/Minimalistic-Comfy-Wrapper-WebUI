

onUiLoaded(() => {
    const progressBar = document.querySelector('#progressBar');
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
    let nodeSegmentsElements = [];


    function voidProgressBar() {
        progressContainer.style.display = "none";
        progressBar.style.width = "0%";
        document.querySelectorAll('.node-progress-segment').forEach(element => {element.remove();});
        nodeSegmentsElements = [];
        TITLE.setProgress(null);
    }


    function connectToProgressSSE() {
        const eventSource = new EventSource('/mcww_api/progress_sse');
        voidProgressBar();

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateProgressContainerWidth();

            if (!data || data.total_progress_percent === null) {
                voidProgressBar();
                return;
            }

            let {
                total_progress_percent,
                node_segments,
                title_text
            } = data;

            node_segments = Object.values(node_segments);
            progressBar.style.width = `${total_progress_percent}%`;

            while (nodeSegmentsElements.length < node_segments.length) {
                const nodeSegmentsElement = document.createElement('div');
                nodeSegmentsElement.className = 'node-progress-segment';
                const width_percent = node_segments[nodeSegmentsElements.length].width_percent;
                const left_percent = node_segments[nodeSegmentsElements.length].left_percent;
                const GAP = 10;
                nodeSegmentsElement.style.width = `calc(${width_percent}% - ${GAP}px)`;
                nodeSegmentsElement.style.left = `calc(${left_percent}% + ${GAP/2}px)`;
                progressContainer.insertBefore(nodeSegmentsElement, progressContainer.firstChild);
                nodeSegmentsElements.push(nodeSegmentsElement);
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

