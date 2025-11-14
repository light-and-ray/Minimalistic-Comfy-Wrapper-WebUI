
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

            const allLabels = Array.from(containerElement.querySelectorAll('label'));
            const draggedIndex = allLabels.indexOf(draggedElement);
            const targetIndex = allLabels.indexOf(targetLabel);

            if (draggedIndex < targetIndex) {
                targetLabel.parentNode.insertBefore(draggedElement, targetLabel.nextSibling);
            } else {
                targetLabel.parentNode.insertBefore(draggedElement, targetLabel);
            }
        }
    }

    function handleDragEnd(event) {
        draggedElement = null;
    }

    const labels = containerElement.querySelectorAll('label');

    labels.forEach((label, index) => {
        if (index === 0) {
            return;
        }

        if (label.dataset.draggableInitialized === 'true') {
            label.removeEventListener('dragstart', handleDragStart);
            label.removeEventListener('dragover', handleDragOver);
            label.removeEventListener('drop', handleDrop);
            label.removeEventListener('dragend', handleDragEnd);
        }

        label.draggable = true;
        label.addEventListener('dragstart', handleDragStart);
        label.addEventListener('dragover', handleDragOver);
        label.addEventListener('drop', handleDrop);
        label.addEventListener('dragend', handleDragEnd);
        label.dataset.draggableInitialized = 'true';
    });
}


function makePresetsRadioDraggable() {
    const radio = document.querySelector(".mcww-presets-radio>div.wrap:not(.default)");
    if (radio) {
        makePresetsRadioDraggableInner(radio);
    }
}

