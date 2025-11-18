// Global variable to hold the background image dimensions
let g_bgImageWidth = 0;
let g_bgImageHeight = 0;

onPageSelected((page) => {
    if (page === "imageEditor") {
        waitForElement("#drawing-canvas", () => applyImageEditor(globalClipboardContent));
    }
});

function openImageEditorPage() {
    selectMainUIPage("imageEditor");
}


var clearImageEditor = null;
var exportDrawing = null;


/**
 * Loads the background image and sets the global dimensions.
 * Then calls resizeCanvas to adjust the canvas elements.
 * @param {File} imageFile The background image file.
 */
function loadImageAndResize(imageFile, resizeCanvas) {
    return new Promise((resolve, reject) => {
        const bgContainer = document.getElementById('image-editor-bg');
        const img = new Image();
        const reader = new FileReader();

        reader.onload = (e) => {
            img.onload = () => {
                // 1. Set global dimensions based on the loaded image
                g_bgImageWidth = img.naturalWidth;
                g_bgImageHeight = img.naturalHeight;

                // 2. Clear container and add the image element
                bgContainer.innerHTML = '';
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'contain'; // Ensure the image fits within the container
                bgContainer.appendChild(img);

                // 3. Resize canvases to match the new image aspect ratio
                resizeCanvas();
                resolve();
            };
            img.onerror = reject;
            img.src = e.target.result;
        };
        reader.onerror = reject;
        reader.readAsDataURL(imageFile);
    });
}


function applyImageEditor(backgroundImageFile) {
    const drawingCanvas = document.getElementById('drawing-canvas');
    const drawCtx = drawingCanvas.getContext('2d');
    const imageCanvas = document.getElementById('image-canvas');
    const imageCtx = imageCanvas.getContext('2d'); // The context for the persistent image layer

    const colorPicker = document.getElementById('colorPicker');

    let isDrawing = false;
    let currentPath = [];
    let fillColor = colorPicker.value;
    const MAX_HEIGHT_VH_RATIO = 0.8;

    // --- Utility Functions ---
    // ... (resizeCanvas and getCoords remain unchanged) ...

    function resizeCanvas() {
        const container = drawingCanvas.parentElement.parentElement;
        const parentWidth = container.clientWidth;

        // Calculate the maximum allowed height based on the CSS constraint (e.g., 80vh)
        const MAX_HEIGHT_PX = window.innerHeight * MAX_HEIGHT_VH_RATIO;

        let targetWidth, targetHeight;
        let aspectRatio = 1; // Default to square if no image is loaded

        if (g_bgImageWidth > 0 && g_bgImageHeight > 0) {
            aspectRatio = g_bgImageWidth / g_bgImageHeight;
        }

        // --- Core Fitting Logic ---
        let heightBasedOnWidth = parentWidth / aspectRatio;

        if (heightBasedOnWidth <= MAX_HEIGHT_PX) {
            targetWidth = parentWidth;
            targetHeight = heightBasedOnWidth;
        } else {
            targetHeight = MAX_HEIGHT_PX;
            targetWidth = targetHeight * aspectRatio;
        }

        // --- Apply Dimensions ---
        const canvasContainer = drawingCanvas.parentElement;
        canvasContainer.style.width = `${targetWidth}px`;
        canvasContainer.style.height = `${targetHeight}px`;

        drawingCanvas.width = targetWidth;
        drawingCanvas.height = targetHeight;
        imageCanvas.width = targetWidth;
        imageCanvas.height = targetHeight;

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

        if (event.type === 'mousedown') {
            window.addEventListener('mousemove', draw);
            window.addEventListener('mouseup', stopDrawing);
        }
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

        if (event.type === 'mouseup' || event.type === 'mouseleave') {
            window.removeEventListener('mousemove', draw);
            window.removeEventListener('mouseup', stopDrawing);
        }

        // 1. Clear the temporary stroke layer immediately
        drawCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);

        if (currentPath.length < 3) {
            currentPath = [];
            return;
        }

        // 2. Commit the filled shape to the permanent image layer (imageCtx)
        imageCtx.beginPath();

        imageCtx.moveTo(currentPath[0].x, currentPath[0].y);

        for (let i = 1; i < currentPath.length; i++) {
            imageCtx.lineTo(currentPath[i].x, currentPath[i].y);
        }

        imageCtx.closePath();

        imageCtx.fillStyle = fillColor;
        imageCtx.fill();

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


    // --- Export Functionality (Remains unchanged) ---
    function getImageFile() {
        return new Promise((resolve, reject) => {
            imageCanvas.toBlob((blob) => {
                if (blob) {
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

    // --- Initial Setup and Event Listeners (MODIFIED) ---

    // Load the background image first, which triggers the initial resizeCanvas call
    if (backgroundImageFile) {
        loadImageAndResize(backgroundImageFile, resizeCanvas);
    } else {
        resizeCanvas();
    }


    // Mouse Events:
    // Only 'mousedown' remains on the canvas to START the drawing.
    // 'mousemove' and 'mouseup' are dynamically added to/removed from the WINDOW.
    // The 'mouseleave' event is now unnecessary for mouse, as 'mouseup' on the window handles stopping.
    drawingCanvas.addEventListener('mousedown', startDrawing);

    // Touch Events on the top drawing layer (Remain unchanged)
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

    clearImageEditor = clearCanvas;
    exportDrawing = handleExport;
}

