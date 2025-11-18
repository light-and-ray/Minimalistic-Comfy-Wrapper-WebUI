
onPageSelected((page) => {
    if (page === "imageEditor") {
        waitForElement("#drawing-canvas", applyImageEditor);
    }
});


function openImageEditorPage() {
    selectMainUIPage("imageEditor");
}


var clearImageEditor = null;
var exportDrawing = null;


function applyImageEditor() {
    const drawingCanvas = document.getElementById('drawing-canvas');
    const drawCtx = drawingCanvas.getContext('2d');
    const imageCanvas = document.getElementById('image-canvas');
    const imageCtx = imageCanvas.getContext('2d'); // The context for the persistent image layer

    const colorPicker = document.getElementById('colorPicker');

    let isDrawing = false;
    let currentPath = [];
    let fillColor = colorPicker.value;

    // --- Utility Functions ---
    function resizeCanvas() {
        const container = drawingCanvas.parentElement;
        const width = container.clientWidth;
        const height = container.clientHeight;

        // Set both canvas element properties
        drawingCanvas.width = width;
        drawingCanvas.height = height;
        imageCanvas.width = width;
        imageCanvas.height = height;

        // Set default stroke style for the temporary drawing line (drawCtx)
        drawCtx.strokeStyle = '#374151'; // Dark gray for the stroke outline
        drawCtx.lineWidth = 2;
        drawCtx.lineJoin = 'round';
        drawCtx.lineCap = 'round';
    }

    // Gets the coordinates from the event (handles both mouse and touch)
    function getCoords(event) {
        const rect = drawingCanvas.getBoundingClientRect();
        let x, y;

        if (event.touches) {
            x = event.touches[0].clientX - rect.left;
            y = event.touches[0].clientY - rect.top;
        } else {
            x = event.clientX - rect.left;
            y = event.clientY - rect.top;
        }

        return { x, y };
    }

    // --- Drawing Logic ---

    function startDrawing(event) {
        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        isDrawing = true;
        currentPath = [];
        const { x, y } = getCoords(event);
        currentPath.push({ x, y });

        drawCtx.beginPath();
        drawCtx.moveTo(x, y);
    }

    function draw(event) {
        if (!isDrawing) return;

        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        const { x, y } = getCoords(event);
        currentPath.push({ x, y });

        // Draw the temporary stroke line on the top canvas (drawCtx)
        drawCtx.lineTo(x, y);
        drawCtx.stroke();
    }

    function stopDrawing(event) {
        if (!isDrawing) return;

        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        isDrawing = false;

        // 1. Clear the temporary stroke layer immediately
        drawCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);

        if (currentPath.length < 3) {
            currentPath = [];
            return;
        }

        // 2. Commit the filled shape to the permanent image layer (imageCtx)
        imageCtx.beginPath();

        // Move to the start point
        imageCtx.moveTo(currentPath[0].x, currentPath[0].y);

        // Draw lines to all subsequent points
        for (let i = 1; i < currentPath.length; i++) {
            imageCtx.lineTo(currentPath[i].x, currentPath[i].y);
        }

        // Close the path (connects back to the start point)
        imageCtx.closePath();

        // Apply the fill color (NO STROKE/OUTLINE)
        imageCtx.fillStyle = fillColor;
        imageCtx.fill();

        // Reset state
        currentPath = [];
    }

    function clearCanvas(fullClear = true) {
        // Always clear the temporary drawing canvas
        drawCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);

        if (fullClear) {
            imageCtx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
            imageCtx.fillStyle = '#ffffff00';
            imageCtx.fillRect(0, 0, imageCanvas.width, imageCanvas.height);
        }
    }

    // --- Export Functionality ---

    /**
     * Returns the contents of the persistent image canvas as a File object.
     * @returns {Promise<File>} A Promise that resolves with the generated File object.
     */
    function getImageFile() {
        return new Promise((resolve, reject) => {
            // Use the permanent image canvas to generate a Blob
            imageCanvas.toBlob((blob) => {
                if (blob) {
                    // Create a File object from the Blob
                    const timestamp = new Date().getTime();
                    const file = new File([blob], `lasso-drawing-${timestamp}.png`, { type: "image/png" });
                    resolve(file);
                } else {
                    reject(new Error("Failed to create blob from canvas."));
                }
            }, 'image/png', 1.0);
        });
    }

    async function handleExport() {
        try {
            const file = await getImageFile();

            // Trigger a download
            const url = URL.createObjectURL(file);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

        } catch (error) {
            console.error("Export Error:", error);
        }
    }

    // --- Event Listeners ---

    // Mouse Events on the top drawing layer
    drawingCanvas.addEventListener('mousedown', startDrawing);
    drawingCanvas.addEventListener('mousemove', draw);
    drawingCanvas.addEventListener('mouseup', stopDrawing);
    drawingCanvas.addEventListener('mouseleave', stopDrawing);

    // Touch Events on the top drawing layer
    drawingCanvas.addEventListener('touchstart', startDrawing);
    drawingCanvas.addEventListener('touchmove', draw);
    drawingCanvas.addEventListener('touchend', stopDrawing);
    drawingCanvas.addEventListener('touchcancel', stopDrawing);

    // Control Listeners
    colorPicker.addEventListener('input', (e) => {
        fillColor = e.target.value;
    });

    // Window Listeners
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    clearImageEditor = clearCanvas;
    exportDrawing = handleExport;
}
