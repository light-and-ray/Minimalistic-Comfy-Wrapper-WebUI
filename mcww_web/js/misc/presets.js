
function openPresetsPage() {
    selectMainUIPage("presets");
}


onPageSelected((page) => {
    if (page === "presets") {
        waitForElement('.refresh-presets', (button) => {
            button.click();
            waitForElement(".after-presets-edited", (button) => {
                button.click();
            })
        })
    }
});


function hidePresetsEditorArrows() {
    const row = document.querySelector('.presets-arrows-row');
    if (row) {
        row.style.display = "none";
    }
}


function makePresetsRadioDraggableInner(containerElement) {
    let draggedElement = null;
    let touchStartTime = null;
    let isLongPress = false;
    const LONG_PRESS_DURATION = 500; // milliseconds
    let touchStartX = 0;
    let touchStartY = 0;

    function handleDragStart(event) {
        if (event.target.tagName === 'LABEL') {
            draggedElement = event.target;
            event.dataTransfer.effectAllowed = 'move';
        } else {
            event.preventDefault();
        }
    }

    function handleDragOver(event) {
        const targetLabel = event.target.closest('label');
        if (targetLabel && containerElement.contains(targetLabel)) {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'move';
        }
    }

    function handleDrop(event) {
        const targetLabel = event.target.closest('label');
        if (draggedElement && draggedElement !== targetLabel && targetLabel?.tagName === 'LABEL' && containerElement.contains(targetLabel)) {
            event.preventDefault();
            event.stopPropagation();
            swapElements(draggedElement, targetLabel);
        }
    }

    function handleDragEnd(event) {
        draggedElement = null;
        isLongPress = false;
    }

    // Touch events for mobile
    function handleTouchStart(event) {
        const label = event.currentTarget;
        if (label.tagName === 'LABEL') {
            touchStartTime = Date.now();
            touchStartX = event.touches[0].clientX;
            touchStartY = event.touches[0].clientY;
            isLongPress = false;

            // Set long press timeout
            label.longPressTimer = setTimeout(() => {
                isLongPress = true;
                draggedElement = label;
                mouseAlert("Drag started");
            }, LONG_PRESS_DURATION);
        }
    }

    function handleTouchMove(event) {
        if (!isLongPress || !draggedElement) return;

        event.preventDefault();
        const touch = event.touches[0];
        const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY);
        const targetLabel = elementBelow?.closest('label');

        if (targetLabel && containerElement.contains(targetLabel) && targetLabel !== draggedElement) {
            targetLabel.style.borderTop = '2px solid var(--presets-radio-drag-and-drop-color)';
        } else {
            // Remove all indicators
            containerElement.querySelectorAll('label').forEach(label => {
                label.style.borderTop = '';
            });
        }
    }

    function handleTouchEnd(event) {
        clearTimeout(draggedElement?.longPressTimer);

        if (isLongPress && draggedElement) {
            const touch = event.changedTouches[0];
            const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY);
            const targetLabel = elementBelow?.closest('label');

            if (targetLabel && draggedElement !== targetLabel && targetLabel?.tagName === 'LABEL' && containerElement.contains(targetLabel)) {
                swapElements(draggedElement, targetLabel);
            }

            containerElement.querySelectorAll('label').forEach(label => {
                label.style.borderTop = '';
            });
        }

        draggedElement = null;
        isLongPress = false;
        touchStartTime = null;
    }

    function swapElements(draggedElement, targetLabel) {
        const allLabels = Array.from(containerElement.querySelectorAll('label'));
        const draggedIndex = allLabels.indexOf(draggedElement);
        const targetIndex = allLabels.indexOf(targetLabel);

        if (draggedIndex < targetIndex) {
            targetLabel.parentNode.insertBefore(draggedElement, targetLabel.nextSibling);
        } else {
            targetLabel.parentNode.insertBefore(draggedElement, targetLabel);
        }
    }

    const labels = containerElement.querySelectorAll('label');
    labels.forEach((label, index) => {
        if (index === 0) {
            return;
        }

        // Remove old listeners if already initialized
        if (label.dataset.draggableInitialized === 'true') {
            label.removeEventListener('dragstart', handleDragStart);
            label.removeEventListener('dragover', handleDragOver);
            label.removeEventListener('drop', handleDrop);
            label.removeEventListener('dragend', handleDragEnd);
            label.removeEventListener('touchstart', handleTouchStart);
            label.removeEventListener('touchmove', handleTouchMove);
            label.removeEventListener('touchend', handleTouchEnd);
        }

        // Mouse drag events
        label.draggable = true;
        label.addEventListener('dragstart', handleDragStart);
        label.addEventListener('dragover', handleDragOver);
        label.addEventListener('drop', handleDrop);
        label.addEventListener('dragend', handleDragEnd);

        // Touch events for mobile
        label.addEventListener('touchstart', handleTouchStart, false);
        label.addEventListener('touchmove', handleTouchMove, false);
        label.addEventListener('touchend', handleTouchEnd, false);

        label.dataset.draggableInitialized = 'true';
    });
}

function makePresetsRadioDraggable() {
    const radio = document.querySelector(".mcww-presets-radio>div.wrap:not(.default)");
    if (radio) {
        makePresetsRadioDraggableInner(radio);
    }
}

