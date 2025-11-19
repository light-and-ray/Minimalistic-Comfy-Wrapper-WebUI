// Global variable to hold the background image dimensions
let g_bgImageWidth = 0;
let g_bgImageHeight = 0;

var globalImageEditorContent = null;
var globalImageEditor = null;
var afterImageEdited = null;

onPageSelected((page) => {
    if (page === "imageEditor") {
        waitForElement("#drawing-canvas", () => {
            if (globalImageEditorContent) {
                globalImageEditor = new ImageEditor(globalImageEditorContent)
                globalImageEditorContent = null;
            } else if (globalImageEditor) {
                const old = globalImageEditor;
                globalImageEditor = new ImageEditor(globalImageEditor.backgroundImage);
                globalImageEditor.historyIndex = old.historyIndex;
                globalImageEditor.history = old.history;
                globalImageEditor.resizeCanvas();
                delete old;
            }
        });
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
        const key = Array.from(column.classList).find(cls => cls.startsWith('mcww-key-'));
        openInEditorButton.onclick = async () => {
            const img = column.querySelector("img");
            if (img) {
                doSaveStates().then(() => {
                    globalImageEditorContent = img;
                    afterImageEdited = async () => {
                        const newImage = await applyDrawing(img, await getImageFile());
                        goBack();
                        waitForElement(`.input-image-column.${key} .upload-container > button`, async (dropButton) => {
                            const dataTransfer = new DataTransfer();
                            dataTransfer.items.add(newImage);
                            const dropEvent = new DragEvent('drop', {
                                dataTransfer: dataTransfer,
                                bubbles: true,
                                cancelable: true,
                            });
                            dropButton.dispatchEvent(dropEvent);
                        });
                    };
                    openImageEditor();
                });
            }

        };
        column.classList.add("listeners-attached");
    });
});


async function applyDrawing(background, drawing) {
    const width = background.naturalWidth || background.width;
    const height = background.naturalHeight || background.height;

    if (width === 0 || height === 0) {
        throw new Error("Background image dimensions are zero. Ensure the image is loaded.");
    }

    const drawingImage = new Image();
    const drawingUrl = URL.createObjectURL(drawing);

    try {
        await new Promise((resolve, reject) => {
            drawingImage.onload = () => {
                URL.revokeObjectURL(drawingUrl); // Clean up the temporary URL
                resolve();
            };
            drawingImage.onerror = () => {
                URL.revokeObjectURL(drawingUrl);
                reject(new Error("Failed to load drawing image."));
            };
            drawingImage.src = drawingUrl;
        });
    } catch (error) {
        console.error(error.message);
        throw error;
    }

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');

    ctx.drawImage(background, 0, 0, width, height);
    ctx.drawImage(drawingImage, 0, 0, width, height);

    const blob = await new Promise(resolve => {
        canvas.toBlob(resolve, 'image/png');
    });

    if (!blob) {
        throw new Error("Failed to create Blob from canvas.");
    }
    const timestamp = new Date().getTime();
    const newFile = new File([blob], `composite_image_${timestamp}.png`, { type: 'image/png', lastModified: Date.now() });

    return newFile;
}


function trySelectTool(toolNumber) {
    const toolButtons = document.querySelectorAll('.image-editor-tools-row button');
    if (toolNumber >= 1 && toolNumber <= toolButtons.length) {
        toolButtons[toolNumber - 1].click();
    }
}


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
var g_Drawing = null;
var undoDrawing = null;
var redoDrawing = null;
var setDrawingTool = null;
var setBrushSize = () => { };
var getImageFile = null;

var lastColorPickerColor = null;



class ImageEditor {
    constructor(backgroundImage) {
        // --- DOM Elements/Contexts (Fields) ---
        this.drawingCanvas = document.getElementById('drawing-canvas');
        this.drawCtx = this.drawingCanvas.getContext('2d');
        this.imageCanvas = document.getElementById('image-canvas');
        this.imageCtx = this.imageCanvas.getContext('2d'); // Persistent layer
        this.previewCanvas = document.getElementById('brush-preview-canvas');
        this.previewCtx = this.previewCanvas.getContext('2d');
        this.bgContainer = document.getElementById('image-editor-bg');

        this.colorPicker = document.getElementById('colorPicker');
        this.brushSizeInput = document.querySelector('#brushSizeInput input[type="range"]');
        this.backgroundImage = backgroundImage;

        // --- State Variables (Fields) ---
        this.isDrawing = false;
        this.currentPath = [];
        this.fillColor = this.colorPicker.value || '#374151';
        this.strokeColor = this.colorPicker.value || '#374151';
        // Base size from UI or default to 5
        this.baseStrokeWidth = this.brushSizeInput ? parseInt(this.brushSizeInput.value) : 5;
        this.currentTool = null;
        this.startPoint = { x: 0, y: 0 };

        // Constants
        this.MAX_HEIGHT_VH_RATIO = 0.8;
        this.MAX_HISTORY_SIZE = 20;

        // --- History Stack Variables ---
        this.history = [];
        this.historyIndex = -1;

        // Global image dimensions (can be set as properties if needed elsewhere)
        this.g_bgImageWidth = 0;
        this.g_bgImageHeight = 0;

        // --- Initialization ---
        this._initialize();
    }

    // --- Private Initialization Method ---

    _initialize() {
        // Restore color picker state if applicable
        if (this.colorPicker.classList.contains("restore") && lastColorPickerColor) {
            this.colorPicker.value = lastColorPickerColor;
            this.fillColor = lastColorPickerColor;
            this.strokeColor = lastColorPickerColor;
        }

        // Determine initial tool based on active button
        const activeToolButton = document.querySelector('.image-editor-tools-row button.primary');
        for (const tool of ["lasso", "brush", "arrow", "eraser"]) {
            if (activeToolButton && activeToolButton.classList.contains(tool)) {
                this.currentTool = tool;
                break;
            }
        }

        // 1. Set global dimensions based on the loaded image
        this.g_bgImageWidth = this.backgroundImage.naturalWidth;
        this.g_bgImageHeight = this.backgroundImage.naturalHeight;

        // 2. Clear container and add the image element
        this.bgContainer.innerHTML = '';
        this.backgroundImage.style.width = '100%';
        this.backgroundImage.style.height = '100%';
        this.backgroundImage.style.objectFit = 'contain';
        this.bgContainer.appendChild(this.backgroundImage);

        // 3. Set canvas dimensions and initial state
        this.resizeCanvas();
        this.saveState();

        // 4. Attach Event Listeners
        this._addEventListeners();
    }

    _addEventListeners() {
        // Bind event handlers to the instance
        this.drawingCanvas.addEventListener('mousedown', this.startDrawing.bind(this));
        this.drawingCanvas.addEventListener('mousemove', this.showCursorPreview.bind(this));
        this.drawingCanvas.addEventListener('mouseleave', this.clearBrushPreview.bind(this));

        this.drawingCanvas.addEventListener('touchstart', this.startDrawing.bind(this));
        this.drawingCanvas.addEventListener('touchmove', this.draw.bind(this));
        this.drawingCanvas.addEventListener('touchend', this.stopDrawing.bind(this));
        this.drawingCanvas.addEventListener('touchcancel', this.stopDrawing.bind(this));

        this.colorPicker.addEventListener('input', this.handleColorChange.bind(this));

        if(this.brushSizeInput) {
            this.brushSizeInput.addEventListener('input', (e) => this.handleBrushSizeChange(parseInt(e.target.value)));
        }

        window.addEventListener('resize', this.resizeCanvas.bind(this));

        // Attach global/public methods to the instance for external access (optional, but follows original structure)
        if (typeof window !== 'undefined') {
            window.clearImageEditor = this.clearCanvas.bind(this);
            window.getImageFile = this.getImageFile.bind(this);
            window.undoDrawing = this.undo.bind(this);
            window.redoDrawing = this.redo.bind(this);
            window.setDrawingTool = this.handleToolChange.bind(this);
            window.setBrushSize = this.handleBrushSizeChange.bind(this);
        }
    }

    // --- Utility Methods ---

    resizeCanvas() {
        const container = this.drawingCanvas.parentElement.parentElement;
        const parentWidth = container.clientWidth;

        const MAX_HEIGHT_PX = window.innerHeight * this.MAX_HEIGHT_VH_RATIO;

        let targetWidth, targetHeight;
        let aspectRatio = 1;

        if (this.g_bgImageWidth > 0 && this.g_bgImageHeight > 0) {
            aspectRatio = this.g_bgImageWidth / this.g_bgImageHeight;
        }

        let heightBasedOnWidth = parentWidth / aspectRatio;

        if (heightBasedOnWidth <= MAX_HEIGHT_PX) {
            targetWidth = parentWidth;
            targetHeight = heightBasedOnWidth;
        } else {
            targetHeight = MAX_HEIGHT_PX;
            targetWidth = targetHeight * aspectRatio;
        }

        const canvasContainer = this.drawingCanvas.parentElement;
        canvasContainer.style.width = `${targetWidth}px`;
        canvasContainer.style.height = `${targetHeight}px`;

        this.drawingCanvas.width = targetWidth;
        this.drawingCanvas.height = targetHeight;
        this.imageCanvas.width = targetWidth;
        this.imageCanvas.height = targetHeight;
        this.previewCanvas.width = targetWidth;
        this.previewCanvas.height = targetHeight;

        // Base drawing context settings for the temporary canvas (lasso stroke)
        this.drawCtx.strokeStyle = '#374151';
        this.drawCtx.lineWidth = 2;
        this.drawCtx.lineJoin = 'round';
        this.drawCtx.lineCap = 'round';
        this.restoreState();
    }

    getCoords(event) {
        const rect = this.drawingCanvas.getBoundingClientRect();
        let x, y;
        if (event.touches) {
            x = event.changedTouches[0].clientX - rect.left;
            y = event.changedTouches[0].clientY - rect.top;
        } else {
            x = event.clientX - rect.left;
            y = event.clientY - rect.top;
        }
        return { x, y };
    }

    // --- History Methods (Public) ---

    saveState() {
        if (this.historyIndex < this.history.length - 1) {
            this.history.splice(this.historyIndex + 1);
        }

        const dataURL = this.imageCanvas.toDataURL('image/png');
        this.history.push(dataURL);
        this.historyIndex = this.history.length - 1;

        if (this.history.length > this.MAX_HISTORY_SIZE) {
            this.history.shift();
            this.historyIndex--;
        }
    }

    restoreState() {
        if (this.historyIndex < 0) {
            this.imageCtx.clearRect(0, 0, this.imageCanvas.width, this.imageCanvas.height);
            return;
        }

        const dataURL = this.history[this.historyIndex];
        const img = new Image();
        img.onload = () => {
            this.imageCtx.clearRect(0, 0, this.imageCanvas.width, this.imageCanvas.height);
            this.imageCtx.drawImage(img, 0, 0, this.imageCanvas.width, this.imageCanvas.height);
        };
        img.src = dataURL;
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.restoreState();
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.restoreState();
        }
    }

    // --- Drawing Helper Methods ---

    drawArrow(ctx, fromX, fromY, toX, toY, color, width) {
        ctx.strokeStyle = color;
        ctx.lineWidth = width;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';

        const headLen = Math.max(8, width * 2);
        const angle = Math.atan2(toY - fromY, toX - fromX);

        ctx.beginPath();
        ctx.moveTo(fromX, fromY);
        ctx.lineTo(toX, toY);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(toX, toY);
        ctx.lineTo(toX - headLen * Math.cos(angle - Math.PI / 6), toY - headLen * Math.sin(angle - Math.PI / 6));
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(toX, toY);
        ctx.lineTo(toX - headLen * Math.cos(angle + Math.PI / 6), toY - headLen * Math.sin(angle + Math.PI / 6));
        ctx.stroke();
    }

    // --- Core Drawing Methods (Event Handlers) ---

    startDrawing(event) {
        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        this.isDrawing = true;
        const coords = this.getCoords(event);
        this.startPoint = coords;
        this.currentPath = [coords];

        let effectiveStrokeWidth = (this.currentTool === 'lasso') ? 2 : this.baseStrokeWidth;

        let tempStrokeColor = this.strokeColor;
        if (this.currentTool === 'lasso') {
            tempStrokeColor = '#374151';
        } else if (this.currentTool === 'eraser') {
            tempStrokeColor = '#ff69b4';
        }

        this.drawCtx.strokeStyle = tempStrokeColor;
        this.drawCtx.lineWidth = effectiveStrokeWidth;
        this.drawCtx.lineJoin = 'round';
        this.drawCtx.lineCap = 'round';

        if (this.currentTool === 'lasso' || this.currentTool === 'brush' || this.currentTool === 'eraser') {
            this.drawCtx.beginPath();
            this.drawCtx.moveTo(coords.x, coords.y);
        }

        // Attach global move/stop listeners for better drawing experience
        if (event.type === 'mousedown') {
            window.addEventListener('mousemove', this._drawBound);
            window.addEventListener('mouseup', this._stopDrawingBound);
            this._drawBound = this.draw.bind(this);
            this._stopDrawingBound = this.stopDrawing.bind(this);
        }
    }

    draw(event) {
        if (!this.isDrawing) return;

        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        const coords = this.getCoords(event);
        const { drawCtx, currentTool, currentPath, startPoint, baseStrokeWidth } = this;

        if (currentTool === 'lasso') {
            currentPath.push(coords);
            drawCtx.lineTo(coords.x, coords.y);
            drawCtx.stroke();

        } else if (currentTool === 'brush' || currentTool === 'eraser') {
            drawCtx.lineTo(coords.x, coords.y);
            drawCtx.stroke();
            drawCtx.beginPath();
            drawCtx.moveTo(coords.x, coords.y);
            currentPath.push(coords);

        } else if (currentTool === 'arrow') {
            drawCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
            this.drawArrow(drawCtx, startPoint.x, startPoint.y, coords.x, coords.y, drawCtx.strokeStyle, baseStrokeWidth);
        }
    }

    stopDrawing(event) {
        if (!this.isDrawing) return;

        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        this.isDrawing = false;
        const endPoint = this.getCoords(event);

        // Clean up global event listeners
        if (this._drawBound) {
            window.removeEventListener('mousemove', this._drawBound);
            window.removeEventListener('mouseup', this._stopDrawingBound);
            this._drawBound = null;
            this._stopDrawingBound = null;
        }


        // 1. Clear the temporary stroke layer
        this.drawCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);

        // 2. Commit the final shape to the permanent image layer
        let effectiveStrokeWidth = (this.currentTool === 'lasso') ? 2 : this.baseStrokeWidth;
        this.imageCtx.globalCompositeOperation = 'source-over'; // Reset operation

        if (this.currentTool === 'lasso') {
            if (this.currentPath.length < 3) {
                this.currentPath = [];
                return;
            }

            this.imageCtx.beginPath();
            this.imageCtx.moveTo(this.currentPath[0].x, this.currentPath[0].y);
            for (let i = 1; i < this.currentPath.length; i++) {
                this.imageCtx.lineTo(this.currentPath[i].x, this.currentPath[i].y);
            }
            this.imageCtx.closePath();
            this.imageCtx.fillStyle = this.fillColor;
            this.imageCtx.fill();

        } else if (this.currentTool === 'brush' || this.currentTool === 'eraser') {
            if (this.currentPath.length < 2) {
                this.currentPath = [];
                return;
            }

            if (this.currentTool === 'eraser') {
                 this.imageCtx.globalCompositeOperation = 'destination-out';
            }

            this.imageCtx.strokeStyle = this.strokeColor;
            this.imageCtx.lineWidth = effectiveStrokeWidth;
            this.imageCtx.lineJoin = 'round';
            this.imageCtx.lineCap = 'round';

            this.imageCtx.beginPath();
            this.imageCtx.moveTo(this.currentPath[0].x, this.currentPath[0].y);
            for (let i = 1; i < this.currentPath.length; i++) {
                this.imageCtx.lineTo(this.currentPath[i].x, this.currentPath[i].y);
            }
            this.imageCtx.stroke();

            this.imageCtx.globalCompositeOperation = 'source-over'; // Reset
        } else if (this.currentTool === 'arrow') {
            this.drawArrow(this.imageCtx, this.startPoint.x, this.startPoint.y, endPoint.x, endPoint.y, this.strokeColor, effectiveStrokeWidth);
        }

        this.saveState();
        this.currentPath = [];
    }

    // --- Brush Preview Methods ---

    drawBrushPreview(x, y, size) {
        this.previewCtx.clearRect(0, 0, this.previewCanvas.width, this.previewCanvas.height);
        this.previewCtx.beginPath();
        this.previewCtx.arc(x, y, size / 2, 0, Math.PI * 2, true);
        this.previewCtx.strokeStyle = '#374151';
        this.previewCtx.lineWidth = 1;
        this.previewCtx.stroke();
    }

    clearBrushPreview() {
        this.previewCtx.clearRect(0, 0, this.previewCanvas.width, this.previewCanvas.height);
    }

    showCursorPreview(event) {
        if (this.currentTool !== 'brush' && this.currentTool !== 'arrow' && this.currentTool !== 'eraser') {
            this.clearBrushPreview();
            return;
        }
        const coords = this.getCoords(event);
        this.drawBrushPreview(coords.x, coords.y, this.baseStrokeWidth);
    }

    showCenterPreview() {
        this.clearBrushPreview();
        const centerX = this.previewCanvas.width / 2;
        const centerY = this.previewCanvas.height / 2;
        this.drawBrushPreview(centerX, centerY, this.baseStrokeWidth);

        if (this.previewTimeout) clearTimeout(this.previewTimeout);
        this.previewTimeout = setTimeout(() => this.clearBrushPreview(), 500);
    }


    // --- Tool/Control Setter Methods (Public) ---

    handleToolChange(toolName) {
        this.currentTool = toolName;
        if (toolName === 'brush' || toolName === 'arrow' || toolName === 'eraser') {
            this.drawingCanvas.style.cursor = 'none';
            this.showCenterPreview();
        } else {
            this.drawingCanvas.style.cursor = 'crosshair';
            this.clearBrushPreview();
        }
    }

    handleColorChange(e) {
        this.fillColor = e.target.value;
        this.strokeColor = e.target.value;
        if (e.target.classList.contains("restore") && typeof lastColorPickerColor !== 'undefined') {
            lastColorPickerColor = e.target.value;
        }
    }

    handleBrushSizeChange(size) {
        this.baseStrokeWidth = size;
        if (this.currentTool === 'brush' || this.currentTool === 'arrow' || this.currentTool === 'eraser') {
            this.showCenterPreview();
        }
    }

    // --- Export Method (Public) ---

    clearCanvas(fullClear = true) {
        this.drawCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);

        if (fullClear) {
            this.imageCtx.clearRect(0, 0, this.imageCanvas.width, this.imageCanvas.height);
            this.saveState();
        }
    }

    getImageFile() {
        return new Promise((resolve, reject) => {
            this.imageCanvas.toBlob((blob) => {
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
}

