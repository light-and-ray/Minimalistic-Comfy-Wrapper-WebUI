
var globalImageEditorForwardedContent = null;
/** @type {ImageEditor} */
var globalImageEditor = null;
var afterImageEdited = null;

onPageSelected((page) => {
    if (page === "image_editor") {
        if (globalImageEditorForwardedContent) {
            if (globalImageEditor) {
                globalImageEditor.cleanup();
                delete globalImageEditor;
            }
            globalImageEditor = new ImageEditor(globalImageEditorForwardedContent);
            globalImageEditorForwardedContent = null;
        }
    }
});

function openImageEditor() {
    selectMainUIPage("image_editor");
}

onUiUpdate((updatedElements) => {
    const columns = updatedElements.querySelectorAll(".input-image-column:not(.listeners-attached)"+
            ":has(button.open-in-image-editor-button)");
    columns.forEach((column) => {
        const openInEditorButton = column.querySelector("button.open-in-image-editor-button");
        const key = Array.from(column.classList).find(cls => cls.startsWith('mcww-key-'));
        openInEditorButton.onclick = async () => {
            const img = column.querySelector("img");
            if (img) {
                doSaveStates().then(() => {
                    globalImageEditorForwardedContent = img;
                    afterImageEdited = async () => {
                        const newImage = await applyDrawing(
                            await awaitImageLoad(globalImageEditor.backgroundImage),
                            await canvasToImageFile(globalImageEditor.imageCanvas),
                            globalImageEditor.getOpacity()
                        );
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
                    column.querySelector(".show-return-button")?.click();
                    openImageEditor();
                });
            }

        };
        column.classList.add("listeners-attached");
    });
});


async function applyDrawing(background, drawing, opacity = 1.0) {
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

    // Draw the background
    ctx.drawImage(background, 0, 0, width, height);

    // Apply opacity to the drawing
    ctx.globalAlpha = opacity;
    ctx.drawImage(drawingImage, 0, 0, width, height);
    ctx.globalAlpha = 1.0; // Reset globalAlpha for future operations

    const blob = await new Promise(resolve => {
        canvas.toBlob(resolve, 'image/png');
    });

    if (!blob) {
        throw new Error("Failed to create Blob from canvas.");
    }

    const timestamp = new Date().getTime();
    let backgroundName = getShortImageName(background.src);
    backgroundName = backgroundName.replace(/\s*- edited\s*\d+$/i, '');
    const newFile = new File([blob], `${backgroundName} - edited ${timestamp}.png`, { type: 'image/png', lastModified: Date.now() });

    return newFile;
}


function trySelectTool(toolNumber) {
    const toolButtons = document.querySelectorAll('.image-editor-tools-row button');
    if (toolNumber >= 1 && toolNumber <= toolButtons.length) {
        toolButtons[toolNumber - 1].click();
    }
}


function tryOpenEditorFromHotkey(imageContainer, forceOpen) {
    const column = imageContainer.closest(".input-image-column");
    if (column) {
        const returnButton = column.querySelector(".return-button");
        if (returnButton && !forceOpen) {
            returnButton.click();
        } else {
            column.querySelector(".open-in-image-editor-button")?.click();
        }
    }
}


var g_Drawing = null;
var lastColorPickerColor = null;


class ImageEditor {
    constructor(backgroundImage) {
        this.PIXELS_SCALE = 2;
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
        this.opacityInput = document.querySelector('.opacity-slider input[type="range"]');
        if (this.opacityInput) {
            this.handleOpacityChange();
        }
        this.backgroundImage = null;
        this._updateBackground(backgroundImage.src, () => this.resizeCanvas());

        // --- State Variables (Fields) ---
        this.isDrawing = false;
        this.currentPath = [];
        this.fillColor = this.colorPicker.value || '#374151';
        this.strokeColor = this.colorPicker.value || '#374151';
        // Base size from UI or default to 5
        this.baseStrokeWidth = this.brushSizeInput ? parseInt(this.brushSizeInput.value) : 5;
        this.baseStrokeWidth *= this.PIXELS_SCALE;
        this.currentTool = null;
        this.startPoint = { x: 0, y: 0 };

        this.MAX_HEIGHT_VH_RATIO = 0.8;
        this.MAX_HISTORY_SIZE = 20;

        this.history = [];
        this.historyIndex = -1;

        // Restore color picker state if applicable
        if (this.colorPicker.classList.contains("restore") && lastColorPickerColor) {
            this.colorPicker.value = lastColorPickerColor;
            this.fillColor = lastColorPickerColor;
            this.strokeColor = lastColorPickerColor;
        }

        // Determine initial tool based on active button
        const activeToolButton = document.querySelector('.image-editor-tools-row button.primary');
        for (const tool of ["lasso", "brush", "arrow", "eraser", "crop"]) {
            if (activeToolButton && activeToolButton.classList.contains(tool)) {
                this.selectDrawingTool(tool);
                break;
            }
        }

        this._listeners = [];
        this.saveState();
        this._addEventListeners();
    }


    _addEventListeners() {
        this._addListener(this.drawingCanvas, 'mousedown', this.startDrawing.bind(this));
        this._addListener(this.drawingCanvas, 'mousemove', this.showCursorPreview.bind(this));
        this._addListener(this.drawingCanvas, 'mouseleave', this.clearBrushPreview.bind(this));
        this._addListener(window, 'mousemove', this.draw.bind(this));
        this._addListener(window, 'mouseup', this.stopDrawing.bind(this));

        this._addListener(this.drawingCanvas, 'touchstart', this.startDrawing.bind(this));
        this._addListener(this.drawingCanvas, 'touchmove', this.draw.bind(this));
        this._addListener(this.drawingCanvas, 'touchend', this.stopDrawing.bind(this));
        this._addListener(this.drawingCanvas, 'touchcancel', this.stopDrawing.bind(this));

        this._addListener(this.colorPicker, 'input', this.handleColorChange.bind(this));

        if(this.brushSizeInput) {
            this._addListener(this.brushSizeInput, 'input', (e) => this.handleBrushSizeChange(parseInt(e.target.value)));
        }
        if(this.opacityInput) {
            this._addListener(this.opacityInput, 'input', (e) => this.handleOpacityChange(parseFloat(e.target.value)));
        }

        this._addListener(window, 'resize', this.resizeCanvas.bind(this))
    }


    _addListener(element, type, handler) {
        const listener = { element, type, handler };
        this._listeners.push(listener);
        element.addEventListener(type, handler);
    }

    cleanup() {
        this._listeners.forEach(({ element, type, handler }) => {
            element.removeEventListener(type, handler);
        });
    }

    _updateBackground(src, onload) {
        this.bgContainer.innerHTML = '';
        this.backgroundImage = document.createElement("img");
        this.backgroundImage.style.width = '100%';
        this.backgroundImage.style.height = '100%';
        this.backgroundImage.style.objectFit = 'contain';
        this.bgContainer.appendChild(this.backgroundImage);
        this.backgroundImage.onload = onload;
        this.backgroundImage.src = src;
    }

    // --- Utility Methods ---

    resizeCanvas() {
        const bgImageWidth = this.backgroundImage.naturalWidth;
        const bgImageHeight = this.backgroundImage.naturalHeight;

        const container = this.drawingCanvas.parentElement.parentElement;
        const parentWidth = container.clientWidth;

        const MAX_HEIGHT_PX = window.screen.height * this.MAX_HEIGHT_VH_RATIO;

        let targetWidth, targetHeight;
        let aspectRatio = 1;

        if (bgImageWidth > 0 && bgImageHeight > 0) {
            aspectRatio = bgImageWidth / bgImageHeight;
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

        this.drawingCanvas.width = targetWidth*this.PIXELS_SCALE;
        this.drawingCanvas.height = targetHeight*this.PIXELS_SCALE;
        this.imageCanvas.width = targetWidth*this.PIXELS_SCALE;
        this.imageCanvas.height = targetHeight*this.PIXELS_SCALE;
        this.previewCanvas.width = targetWidth*this.PIXELS_SCALE;
        this.previewCanvas.height = targetHeight*this.PIXELS_SCALE;

        this.drawCtx.strokeStyle = '#374151';
        this.drawCtx.lineWidth = 2*this.PIXELS_SCALE;
        this.drawCtx.lineJoin = 'round';
        this.drawCtx.lineCap = 'round';

        this.restoreState(/* fromResizeCanvas */true);
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
        x *= this.PIXELS_SCALE;
        y *= this.PIXELS_SCALE;
        return { x, y };
    }

    // --- History Methods (Public) ---

    async saveCurrentStateBackground() {
        await awaitImageLoad(this.backgroundImage);
        this.history[this.historyIndex].background = await imgUrlToFile(this.backgroundImage.src);
    }

    saveState() {
        if (this.historyIndex < this.history.length - 1) {
            this.history.splice(this.historyIndex + 1);
        }
        const dataURL = this.imageCanvas.toDataURL('image/png');
        this.history.push({
            canvas: dataURL,
            background: null,
        });

        this.historyIndex = this.history.length - 1;
        if (this.history.length > this.MAX_HISTORY_SIZE) {
            this.history.shift();
            this.historyIndex--;
        }
    }

    restoreState(fromResizeCanvas = false) {
        if (this.historyIndex < 0) {
            this.imageCtx.clearRect(0, 0, this.imageCanvas.width, this.imageCanvas.height);
            return;
        }
        const state = this.history[this.historyIndex];
        const img = new Image();
        img.onload = () => {
            this.imageCtx.clearRect(0, 0, this.imageCanvas.width, this.imageCanvas.height);
            this.imageCtx.drawImage(img, 0, 0, this.imageCanvas.width, this.imageCanvas.height);
            if (state.background && !fromResizeCanvas) {
                this._updateBackground(URL.createObjectURL(state.background), () => {
                    console.log("background updated from restoreState");
                    this.resizeCanvas();
                });
            }
        };
        img.src = state.canvas;
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

    drawRect(ctx, fromX, fromY, toX, toY, color, width) {
        ctx.strokeStyle = color;
        ctx.lineWidth = width;
        ctx.lineJoin = 'miter';
        ctx.lineCap = 'square';

        // Calculate the width and height of the rectangle
        const rectWidth = toX - fromX;
        const rectHeight = toY - fromY;

        ctx.beginPath();
        ctx.rect(fromX, fromY, rectWidth, rectHeight);
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

        const ignoreBrush = ["lasso", "crop"].includes(this.currentTool);
        let effectiveStrokeWidth = ignoreBrush ? 2 : this.baseStrokeWidth;

        let tempStrokeColor = this.strokeColor;
        if (ignoreBrush) {
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
        } else if (currentTool === 'crop') {
            drawCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
            this.drawRect(drawCtx, startPoint.x, startPoint.y, coords.x, coords.y, drawCtx.strokeStyle, 4);
        }
    }

    stopDrawing(event) {
        if (!this.isDrawing) return;

        if (event.type.startsWith('touch')) {
            event.preventDefault();
        }

        this.isDrawing = false;
        const endPoint = this.getCoords(event);

        // 1. Clear the temporary stroke layer
        this.drawCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);

        // 2. Commit the final shape to the permanent image layer
        const ignoreBrush = ["lasso", "crop"].includes(this.currentTool);
        let effectiveStrokeWidth = ignoreBrush ? 2 : this.baseStrokeWidth;
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
            const MIN_PATH_POINTS_FOR_STROKE = 2;
            if (this.currentPath.length < 1) {
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

            if (this.currentPath.length < MIN_PATH_POINTS_FOR_STROKE) {
                const startPoint = this.currentPath[0];
                this.imageCtx.fillStyle = this.strokeColor;
                this.imageCtx.beginPath();
                this.imageCtx.arc(startPoint.x, startPoint.y, effectiveStrokeWidth / 2, 0, 2 * Math.PI);
                this.imageCtx.fill();

            } else {
                this.imageCtx.beginPath();
                this.imageCtx.moveTo(this.currentPath[0].x, this.currentPath[0].y);
                for (let i = 1; i < this.currentPath.length; i++) {
                    this.imageCtx.lineTo(this.currentPath[i].x, this.currentPath[i].y);
                }
                this.imageCtx.stroke();
            }

            this.imageCtx.globalCompositeOperation = 'source-over'; // Reset
        } else if (this.currentTool === 'arrow') {
            const dx = endPoint.x - this.startPoint.x;
            const dy = endPoint.y - this.startPoint.y;
            const distanceSquared = dx * dx + dy * dy;
            const threshold = 5;
            if (distanceSquared >= threshold*threshold) {
                this.drawArrow(this.imageCtx, this.startPoint.x, this.startPoint.y, endPoint.x, endPoint.y, this.strokeColor, effectiveStrokeWidth);
            }
        } else if (this.currentTool === 'crop') {
            this.crop(this.startPoint.x, this.startPoint.y, endPoint.x, endPoint.y);
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
        this.previewCtx.lineWidth = 1*this.PIXELS_SCALE;
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

    selectDrawingTool(toolName) {
        this.currentTool = toolName;
        if (["brush", "arrow", "eraser"].includes(toolName)) {
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

    getOpacity() {
        return this.opacityInput.value;
    }

    handleBrushSizeChange(size) {
        this.baseStrokeWidth = size*this.PIXELS_SCALE;
        this.showCenterPreview();
    }

    handleOpacityChange() {
        this.imageCanvas.style.opacity = this.getOpacity();
        this.drawingCanvas.style.opacity = this.getOpacity();
    }

    clearCanvas(fullClear = true) {
        this.drawCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);

        if (fullClear) {
            this.imageCtx.clearRect(0, 0, this.imageCanvas.width, this.imageCanvas.height);
            this.saveState();
        }
    }


    async rotate() {
        const img = this.backgroundImage;
        if (!img) {
            console.error('No image found inside the container.');
            return;
        }
        await this.saveCurrentStateBackground();

        // Rotate the background image
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.naturalHeight;
        canvas.height = img.naturalWidth;
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(Math.PI / 2);
        ctx.drawImage(img, -img.naturalWidth / 2, -img.naturalHeight / 2);

        this._updateBackground(canvas.toDataURL('image/png'), async () => {
            console.log("background updated from rotate");
            // Rotate this.imageCanvas and this.imageCtx
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');
            tempCanvas.width = this.imageCanvas.height;
            tempCanvas.height = this.imageCanvas.width;
            tempCtx.translate(tempCanvas.width / 2, tempCanvas.height / 2);
            tempCtx.rotate(Math.PI / 2);
            tempCtx.drawImage(this.imageCanvas, -this.imageCanvas.width / 2, -this.imageCanvas.height / 2);

            // Clear and resize the original canvas
            this.imageCanvas.width = tempCanvas.width;
            this.imageCanvas.height = tempCanvas.height;

            // Draw the rotated content back to the original canvas
            this.imageCtx.drawImage(tempCanvas, 0, 0);

            // Now the image is fully updated
            this.saveState();
            await this.saveCurrentStateBackground();
            this.resizeCanvas();
        });
    }


    async crop(startX, startY, endX, endY) {
        const img = this.backgroundImage;
        if (!img) {
            console.error('No image found inside the container.');
            return;
        }

        // Ensure coordinates are valid
        const width = Math.abs(endX - startX);
        const height = Math.abs(endY - startY);
        if (width === 0 || height === 0) {
            console.error('Invalid crop dimensions.');
            return;
        }

        await this.saveCurrentStateBackground();

        // Calculate scaling factors for the background image
        const scaleX = img.naturalWidth / this.imageCanvas.width;
        const scaleY = img.naturalHeight / this.imageCanvas.height;

        // Scale coordinates for the background image
        const bgStartX = Math.min(startX, endX) * scaleX;
        const bgStartY = Math.min(startY, endY) * scaleY;
        const bgWidth = width * scaleX;
        const bgHeight = height * scaleY;

        // Crop the background image
        const bgCanvas = document.createElement('canvas');
        const bgCtx = bgCanvas.getContext('2d');
        bgCanvas.width = bgWidth;
        bgCanvas.height = bgHeight;
        bgCtx.drawImage(
            img,
            bgStartX, bgStartY,  // Source x and y (scaled)
            bgWidth, bgHeight,   // Source width and height (scaled)
            0, 0,                // Destination x and y
            bgWidth, bgHeight    // Destination width and height
        );

        // Update the background with the cropped image
        this._updateBackground(bgCanvas.toDataURL('image/png'), async () => {
            console.log("Background updated from crop");

            // Crop the drawing canvas (this.imageCanvas)
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');
            tempCanvas.width = width;
            tempCanvas.height = height;
            tempCtx.drawImage(
                this.imageCanvas,
                Math.min(startX, endX), // Source x (canvas space)
                Math.min(startY, endY), // Source y (canvas space)
                width, height,          // Source width and height (canvas space)
                0, 0,                   // Destination x and y
                width, height           // Destination width and height
            );

            // Clear and resize the original canvas
            this.imageCanvas.width = tempCanvas.width;
            this.imageCanvas.height = tempCanvas.height;

            // Draw the cropped content back to the original canvas
            this.imageCtx.drawImage(tempCanvas, 0, 0);

            // Save the state and resize the canvas
            this.saveState();
            await this.saveCurrentStateBackground();
            this.resizeCanvas();
        });
    }

}

