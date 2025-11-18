// Global variable to hold the background image dimensions
let g_bgImageWidth = 0;
let g_bgImageHeight = 0;

var globalImageEditorContent = null;
var afterImageEdited = null;

onPageSelected((page) => {
    if (page === "imageEditor") {
        waitForElement("#drawing-canvas", () => {
            applyImageEditor(globalImageEditorContent)
        });
    } else {
        if (afterImageEdited) {
            afterImageEdited();
            afterImageEdited = null;
        }
    }
});

function openImageEditor() {
    selectMainUIPage("imageEditor");
}

onUiUpdate(() => {
    const columns = document.querySelectorAll(".input-image-column:not(.listeners-attached)"+
            ":has(button.open-in-image-editor-button)");
    columns.forEach((column) => {
        const openInEditorButton = column.querySelector("button.open-in-image-editor-button");
        openInEditorButton.onclick = async () => {
            const img = column.querySelector("img");
            if (img) {
                doSaveStates().then(() => {
                    globalImageEditorContent = img;
                    openImageEditor();
                });
            }

        };
        column.classList.add("listeners-attached");
    });
});


function selectLassoTool() {
    setDrawingTool("lasso");
}
function selectBrushTool() {
    setDrawingTool("brush");
}
function selectArrowTool() {
    setDrawingTool("arrow");
}
function selectEraserTool() {
    setDrawingTool("eraser");
}


var clearImageEditor = null;
var exportDrawing = null;
var undoDrawing = null;
var redoDrawing = null;
var setDrawingTool = null;
var setBrushSize = () => { };


async function applyImageEditor(backgroundImage) {
    const drawingCanvas = document.getElementById('drawing-canvas');
    const drawCtx = drawingCanvas.getContext('2d');
    const imageCanvas = document.getElementById('image-canvas');
    const imageCtx = imageCanvas.getContext('2d'); // The context for the persistent image layer
    const previewCanvas = document.getElementById('brush-preview-canvas');
    const previewCtx = previewCanvas.getContext('2d');

    // Background container reference
    const bgContainer = document.getElementById('image-editor-bg');

    const colorPicker = document.getElementById('colorPicker');
    const brushSizeInput = document.querySelector('#brushSizeInput input[type="range"]');

    let isDrawing = false;
    let currentPath = [];
    // RESET: Set initial colors to a neutral default
    let fillColor = colorPicker.value || '#374151';
    let strokeColor = colorPicker.value || '#374151';
    let baseStrokeWidth = brushSizeInput ? parseInt(brushSizeInput.value) : 5; // Base size from UI
    const MAX_HEIGHT_VH_RATIO = 0.8;

    let currentTool = 'lasso';
    let startPoint = { x: 0, y: 0 };

    // --- History Stack Variables for Undo/Redo ---
    const history = [];
    let historyIndex = -1;
    const MAX_HISTORY_SIZE = 20;

    // --- Utility Functions ---

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

        previewCanvas.width = targetWidth;
        previewCanvas.height = targetHeight;

        // Base drawing context settings for the temporary canvas (lasso stroke)
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
            // Use changedTouches for touchend events
            x = event.changedTouches[0].clientX - rect.left;
            y = event.changedTouches[0].clientY - rect.top;
        } else {
            x = event.clientX - rect.left;
            y = event.clientY - rect.top;
        }
        return { x, y };
    }

    // --- History Functions ---
    function saveState() {
        if (historyIndex < history.length - 1) {
            history.splice(historyIndex + 1);
        }

        // Get a data URL snapshot of the image canvas
        const dataURL = imageCanvas.toDataURL('image/png');
        history.push(dataURL);
        historyIndex = history.length - 1;

        // Limit history size
        if (history.length > MAX_HISTORY_SIZE) {
            history.shift(); // Remove the oldest state
            historyIndex--;
        }
    }

    function restoreState() {
        if (historyIndex < 0) {
            // If no history, just clear the canvas fully (initial state)
            imageCtx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
            return;
        }

        const dataURL = history[historyIndex];
        const img = new Image();
        img.onload = () => {
            imageCtx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
            imageCtx.drawImage(img, 0, 0, imageCanvas.width, imageCanvas.height);
        };
        img.src = dataURL;
    }

    function undo() {
        if (historyIndex > 0) {
            historyIndex--;
            restoreState();
        }
    }

    function redo() {
        if (historyIndex < history.length - 1) {
            historyIndex++;
            restoreState();
        }
    }


    // --- ARROW Drawing Implementation ---
    function drawArrow(ctx, fromX, fromY, toX, toY, color, width) {
        // Set context for drawing
        ctx.strokeStyle = color;
        ctx.lineWidth = width;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';

        const headLen = Math.max(8, width * 2); // Length of the lines at the tip
        const angle = Math.atan2(toY - fromY, toX - fromX);

        ctx.beginPath();

        // 1. Draw the main line
        ctx.moveTo(fromX, fromY);
        ctx.lineTo(toX, toY);
        ctx.stroke();

        // 2. Draw the two lines for the tip
        ctx.beginPath();
        // Right side of the tip
        ctx.moveTo(toX, toY);
        ctx.lineTo(toX - headLen * Math.cos(angle - Math.PI / 6), toY - headLen * Math.sin(angle - Math.PI / 6));
        ctx.stroke();

        // Left side of the tip
        ctx.beginPath();
        ctx.moveTo(toX, toY);
        ctx.lineTo(toX - headLen * Math.cos(angle + Math.PI / 6), toY - headLen * Math.sin(angle + Math.PI / 6));
        ctx.stroke();
    }


    // --- Drawing Logic ---

    function startDrawing(event) {
        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        isDrawing = true;
        const coords = getCoords(event);
        startPoint = coords;
        currentPath = [coords];

        let effectiveStrokeWidth = (currentTool === 'lasso') ? 2 : baseStrokeWidth;

        let tempStrokeColor = strokeColor;
        if (currentTool === 'lasso') {
            tempStrokeColor = '#374151'; // Dark grey for lasso outline
        } else if (currentTool === 'eraser') {
            tempStrokeColor = '#ff69b4'; // Pink for eraser context
        }

        // Setup the temporary canvas context for the current tool's visual
        drawCtx.strokeStyle = tempStrokeColor;
        drawCtx.lineWidth = effectiveStrokeWidth;
        drawCtx.lineJoin = 'round';
        drawCtx.lineCap = 'round';

        if (currentTool === 'lasso' || currentTool === 'brush' || currentTool === 'eraser') {
            drawCtx.beginPath();
            drawCtx.moveTo(coords.x, coords.y);
        }

        // Attach move/stop listeners to the window for better drawing experience
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

        const coords = getCoords(event);

        if (currentTool === 'lasso') {
            currentPath.push(coords);
            // Draw the temporary stroke line on the top canvas (drawCtx)
            drawCtx.lineTo(coords.x, coords.y);
            drawCtx.stroke();

        } else if (currentTool === 'brush' || currentTool === 'eraser') {
            // Draw immediately to the temporary canvas
            drawCtx.lineTo(coords.x, coords.y);
            drawCtx.stroke();
            drawCtx.beginPath();
            drawCtx.moveTo(coords.x, coords.y); // start a new path segment
            currentPath.push(coords);

        } else if (currentTool === 'arrow') {
            // Live preview: Clear temp canvas and redraw arrow
            drawCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
            let effectiveStrokeWidth = (currentTool === 'lasso') ? 2 : baseStrokeWidth;
            drawArrow(drawCtx, startPoint.x, startPoint.y, coords.x, coords.y, drawCtx.strokeStyle, effectiveStrokeWidth);
        }
    }

    function stopDrawing(event) {
        if (!isDrawing) return;

        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        isDrawing = false;
        const endPoint = getCoords(event);

        // Clean up window event listeners
        if (event.type === 'mouseup' || event.type === 'mouseleave') {
            window.removeEventListener('mousemove', draw);
            window.removeEventListener('mouseup', stopDrawing);
        }

        // 1. Clear the temporary stroke layer immediately
        drawCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);

        // 2. Commit the final shape to the permanent image layer (imageCtx)
        let effectiveStrokeWidth = (currentTool === 'lasso') ? 2 : baseStrokeWidth;

        // Reset composite operation before drawing permanent shapes
        imageCtx.globalCompositeOperation = 'source-over';

        if (currentTool === 'lasso') {
            if (currentPath.length < 3) {
                currentPath = [];
                return;
            }

            imageCtx.beginPath();
            imageCtx.moveTo(currentPath[0].x, currentPath[0].y);
            for (let i = 1; i < currentPath.length; i++) {
                imageCtx.lineTo(currentPath[i].x, currentPath[i].y);
            }
            imageCtx.closePath();
            imageCtx.fillStyle = fillColor;
            imageCtx.fill();

        } else if (currentTool === 'brush' || currentTool === 'eraser') {
            if (currentPath.length < 2) {
                currentPath = [];
                return;
            }

            // Set composite operation for erasing
            if (currentTool === 'eraser') {
                 imageCtx.globalCompositeOperation = 'destination-out';
            }

            // Redraw the path on the permanent canvas
            imageCtx.strokeStyle = strokeColor;
            imageCtx.lineWidth = effectiveStrokeWidth;
            imageCtx.lineJoin = 'round';
            imageCtx.lineCap = 'round';

            imageCtx.beginPath();
            imageCtx.moveTo(currentPath[0].x, currentPath[0].y);
            for (let i = 1; i < currentPath.length; i++) {
                imageCtx.lineTo(currentPath[i].x, currentPath[i].y);
            }
            imageCtx.stroke();

            // Reset composite operation
            imageCtx.globalCompositeOperation = 'source-over';

        } else if (currentTool === 'arrow') {
            // Draw the final arrow on the permanent canvas
            drawArrow(imageCtx, startPoint.x, startPoint.y, endPoint.x, endPoint.y, strokeColor, effectiveStrokeWidth);
        }

        saveState();
        currentPath = [];
    }

    function clearCanvas(fullClear = true) {
        // Always clear the temporary drawing canvas
        drawCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);

        if (fullClear) {
            imageCtx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
            saveState();
        }
    }

    // --- Brush Preview Functions ---

    let previewTimeout;

    function drawBrushPreview(x, y, size) {
        previewCtx.clearRect(0, 0, previewCanvas.width, previewCanvas.height);
        previewCtx.beginPath();
        previewCtx.arc(x, y, size / 2, 0, Math.PI * 2, true); // size is the diameter
        previewCtx.strokeStyle = '#374151';
        previewCtx.lineWidth = 1;
        previewCtx.stroke();
    }

    function clearBrushPreview() {
        previewCtx.clearRect(0, 0, previewCanvas.width, previewCanvas.height);
    }

    function showCursorPreview(event) {
        if (currentTool !== 'brush' && currentTool !== 'arrow' && currentTool !== 'eraser') {
            clearBrushPreview();
            return;
        }
        const coords = getCoords(event);
        drawBrushPreview(coords.x, coords.y, baseStrokeWidth);
    }

    function showCenterPreview() {
        clearBrushPreview();
        const centerX = previewCanvas.width / 2;
        const centerY = previewCanvas.height / 2;
        drawBrushPreview(centerX, centerY, baseStrokeWidth);

        // Clear the center preview after a short duration
        if (previewTimeout) clearTimeout(previewTimeout);
        previewTimeout = setTimeout(clearBrushPreview, 500); // 500ms duration
    }


    // --- Tool and Color/Size Controls ---
    function handleToolChange(toolName) {
        currentTool = toolName;
        if (toolName === 'brush' || toolName === 'arrow' || toolName === 'eraser') {
            drawingCanvas.style.cursor = 'none'; // Hide default cursor
        } else {
            drawingCanvas.style.cursor = 'crosshair';
            clearBrushPreview();
        }
    }

    function handleColorChange(e) {
        // Only update permanent colors. The temporary draw color is handled in startDrawing
        fillColor = e.target.value;
        strokeColor = e.target.value;
    }

    function handleBrushSizeChange(size) {
        baseStrokeWidth = size;
        if (currentTool === 'brush' || currentTool === 'arrow' || currentTool === 'eraser') {
            showCenterPreview();
        }
    }

    // --- Export Functionality ---
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


    // 1. Set global dimensions based on the loaded image
    // Assuming the image is already loaded (check should happen before calling this function)
    g_bgImageWidth = backgroundImage.naturalWidth;
    g_bgImageHeight = backgroundImage.naturalHeight;

    // 2. Clear container and add the image element
    bgContainer.innerHTML = '';
    backgroundImage.style.width = '100%';
    backgroundImage.style.height = '100%';
    backgroundImage.style.objectFit = 'contain';
    bgContainer.appendChild(backgroundImage);

    resizeCanvas();
    saveState();

    // Mouse Events:
    drawingCanvas.addEventListener('mousedown', startDrawing);
    drawingCanvas.addEventListener('mousemove', showCursorPreview);
    drawingCanvas.addEventListener('mouseleave', clearBrushPreview);

    // Touch Events on the top drawing layer
    drawingCanvas.addEventListener('touchstart', startDrawing);
    drawingCanvas.addEventListener('touchmove', draw);
    drawingCanvas.addEventListener('touchend', stopDrawing);
    drawingCanvas.addEventListener('touchcancel', stopDrawing);

    // Control Listeners
    colorPicker.addEventListener('input', handleColorChange);

    if(brushSizeInput) {
        brushSizeInput.addEventListener('input', handleBrushSizeChange);
    }

    // Window Listeners
    window.addEventListener('resize', resizeCanvas);

    // Global variable assignments
    clearImageEditor = clearCanvas;
    exportDrawing = handleExport;
    undoDrawing = undo;
    redoDrawing = redo;
    setDrawingTool = handleToolChange;
    setBrushSize = handleBrushSizeChange;
}

