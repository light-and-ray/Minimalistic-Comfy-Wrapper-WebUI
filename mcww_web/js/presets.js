
function openPresetsPage() {
    selectMainUIPage("presets");
}

var needRunAfterPresetsEditedCallback = false;

onPageSelected((page) => {
    if (page === "presets") {
        waitForElement('.refresh-presets', (button) => {
            needRunAfterPresetsEditedCallback = true;
            button.click();
        })
    } else {
        if (needRunAfterPresetsEditedCallback) {
            needRunAfterPresetsEditedCallback = false;
            waitForElement(".after-presets-edited", (button) => {
                button.click();
            })
        }
    }
});


function makePresetsRadioDraggableInner(containerElement, afterDrag) {
    let draggedElement = null;
    let touchStartTime = null;
    let isLongPress = false;
    const LONG_PRESS_DURATION = 500;
    const TOUCH_MOVE_THRESHOLD = 10; // pixels
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
        effectOnDragOver(targetLabel);
        if (targetLabel && containerElement.contains(targetLabel)) {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'move';
        }
    }

    function handleDrop(event) {
        const targetLabel = event.target.closest('label');
        effectOnDragOver(null);
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
            draggedElement = label;
            // Set long press timeout
            label.longPressTimer = setTimeout(() => {
                isLongPress = true;
            }, LONG_PRESS_DURATION);
        }
    }

    function handleTouchMove(event) {
        if (!draggedElement) return;

        const touch = event.touches[0];
        const deltaX = Math.abs(touch.clientX - touchStartX);
        const deltaY = Math.abs(touch.clientY - touchStartY);
        const hasMovedBeyondThreshold = deltaX > TOUCH_MOVE_THRESHOLD || deltaY > TOUCH_MOVE_THRESHOLD;

        // Cancel long press if movement detected BEFORE long press activates
        if (hasMovedBeyondThreshold && !isLongPress && draggedElement?.longPressTimer) {
            clearTimeout(draggedElement.longPressTimer);
            draggedElement = null;
            return;
        }

        // Only apply drag visual feedback if long press is confirmed
        if (!isLongPress || !draggedElement) return;
        event.preventDefault();
        const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY);
        const targetLabel = elementBelow?.closest('label');
        effectOnDragOver(targetLabel);
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
            effectOnDragOver(null);
        }
        draggedElement = null;
        isLongPress = false;
        touchStartTime = null;
    }

    function isLeft(targetLabel) {
        const allLabels = Array.from(containerElement.querySelectorAll('label'));
        const draggedIndex = allLabels.indexOf(draggedElement);
        const targetIndex = allLabels.indexOf(targetLabel);
        if (draggedIndex < targetIndex) {
            return false;
        } else {
            return true;
        }
    }

    function swapElements(draggedElement, targetLabel) {
        if (isLeft(targetLabel)) {
            targetLabel.parentNode.insertBefore(draggedElement, targetLabel);
        } else {
            targetLabel.parentNode.insertBefore(draggedElement, targetLabel.nextSibling);
        }
        afterDrag();
    }

    const activeBorderStyle = '2px solid var(--presets-radio-drag-and-drop-color)';
    function effectOnDragOver(targetLabel) {
        containerElement.querySelectorAll('label').forEach(label => {
            label.style.borderTop = '';
            label.classList.remove('drag-left-line', 'drag-right-line');
        });
        if (targetLabel && containerElement.contains(targetLabel) && targetLabel !== draggedElement) {
            targetLabel.style.borderTop = activeBorderStyle;
            if (isLeft(targetLabel)) {
                targetLabel.classList.add('drag-left-line');
            } else {
                targetLabel.classList.add('drag-right-line');
            }
        }
    }

    const labels = containerElement.querySelectorAll('label');
    labels.forEach((label, index) => {
        if (index === 0) {
            return;
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


function afterPresetDrag(radio) {
    const spans = radio.querySelectorAll('label span');
    const newOrderTextbox = document.querySelector('.presets-new-order-after-drag textarea');
    const spanContents = Array.from(spans).map(span => span.textContent);
    const jsonList = JSON.stringify(spanContents);

    if (newOrderTextbox) {
        newOrderTextbox.value = jsonList;
        const event = new Event('input', { bubbles: true });
        newOrderTextbox.dispatchEvent(event);
    }
}


function makePresetsRadioDraggable(updatedElements) {
    const radio = updatedElements.querySelector(".mcww-presets-radio>div.wrap:not(.default):not(.patched");
    if (radio) {
        makePresetsRadioDraggableInner(radio, () => {afterPresetDrag(radio)});
        radio.classList.add('patched');
    }
}

onUiUpdate(makePresetsRadioDraggable);


class _ScrollToPresetsDataset {
    constructor() {
        this._storedDiffPosition = null;
    }

    _getDatasetTop() {
        return document.querySelector(".presets-dataset").getBoundingClientRect().top;
    }

    storePosition() {
        this._storedDiffPosition = this._getDatasetTop() - window.pageYOffset;
    }

    scrollToStoredPosition() {
        const currentPosition = this._getDatasetTop();
        window.scrollTo({
            top: currentPosition - this._storedDiffPosition,
        });
    }
}

var scrollToPresetsDataset = new _ScrollToPresetsDataset()

onUiUpdate((updatedElements) => {
    const presetsDataset = updatedElements.querySelector('.presets-dataset:not(.patched)');
    if (presetsDataset) {
        const presetsDatasetDiv = presetsDataset.querySelector('div');
        presetsDataset.classList.add("patched");
        const isMobile = window.matchMedia('(max-width: 767px)').matches;
        const initialHeight = isMobile ? 193 : 118;
        const contentHeight = presetsDataset.scrollHeight;
        presetsDataset.style.height = `${Math.min(contentHeight, initialHeight)}px`;
        presetsDataset.style.minHeight = `${Math.min(contentHeight, 50)}px`;
        presetsDataset.style.maxHeight = `${contentHeight}px`;
        if (contentHeight < initialHeight) {
            presetsDatasetDiv.style.overflowY = "hidden";
        }
        const onResize = () => {
            presetsDatasetDiv.style.maxHeight = presetsDataset.style.height;
        };
        onResize();
        addOnResizeCallback(presetsDataset, onResize);
    }}
);
