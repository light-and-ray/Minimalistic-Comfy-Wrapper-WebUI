
function applyMcwwQueueJson() {
    // Find the fieldset containing the radio labels
    const fieldset = document.querySelector('fieldset.mcww-queue-radio');
    if (!fieldset) {
        return;
    }

    // Find the textarea containing the JSON
    const textarea = document.querySelector('.mcww-queue-json textarea');
    if (!textarea) {
        console.error('No .mcww-queue-json textarea found');
        return;
    }

    let json;
    try {
        json = JSON.parse(textarea.value);
    } catch (e) {
        console.error('Invalid JSON in .mcww-queue-json textarea', e);
        return;
    }

    // Process each label in the fieldset
    const labels = fieldset.querySelectorAll('label');
    labels.forEach(label => {
        const span = label.querySelector('span');
        if (!span) return;

        span.classList.add("mcww-hidden");
        label.querySelectorAll('.queue-content').forEach(element => {
            element.remove();
        });

        const key = span.textContent.trim();
        if (key === '-1') {
            label.classList.add('mcww-hidden');
            return;
        } else {
            label.classList.remove('mcww-hidden');
        }

        const data = json[key];
        if (!data) return;

        // Clear the span
        contentDiv = document.createElement('div')
        contentDiv.classList.add("queue-content");
        span.parentElement.appendChild(contentDiv);

        // Add media if present
        if (data.fileUrl) {
            const fileUrl = data.fileUrl.toLowerCase();

            if (isImageUrl(fileUrl)) {
                const img = document.createElement('img');
                img.src = data.fileUrl;
                contentDiv.appendChild(img);
            }
            else if (isVideoUrl(fileUrl)) {
                const video = document.createElement('video');
                video.src = data.fileUrl;
                video.controls = false;
                video.autoplay = false;
                video.preload = "metadata";
                contentDiv.appendChild(video);
            }
        }

        // Add text (wrapped in a div for styling)
        const textDiv = document.createElement('div');
        textDiv.textContent = data.text;
        textDiv.classList.add('mcww-text');
        contentDiv.appendChild(textDiv);

        // Add ID in the bottom right corner
        const idDiv = document.createElement('div');
        idDiv.textContent = data.id;
        idDiv.classList.add('mcww-id');
        contentDiv.appendChild(idDiv);

        // Add status as a class to the label
        label.classList.remove("in_progress", "queued", "complete", "error");
        if (data.status) {
            label.classList.add(data.status);
        }
    });
    fieldset.classList.remove('mcww-hidden');
}


function getPreviousLabel(labels) {
    let previousLabel = null;
    let selectedLabel = null;
    for (const label of labels) {
        if (label.matches('.selected')) {
            selectedLabel = label;
            break;
        }
        previousLabel = label;
    }
    return previousLabel;
}


function getNextLabel(labels) {
    let selectedLabel = null;
    let nextLabel = null;
    for (const label of labels) {
        if (selectedLabel) {
            nextLabel = label;
            break;
        }
        if (label.matches('.selected')) {
            selectedLabel = label;
        }
    }
    return nextLabel;
}


function trySelectPreviousQueueEntry() {
    const fieldset = document.querySelector('fieldset.mcww-queue-radio');
    if (!uiElementIsVisible(fieldset)) {
        return;
    }
    const labels = fieldset.querySelectorAll('label');
    if (!labels) {
        return;
    }

    const previousLabel = getPreviousLabel(labels);

    if (previousLabel) {
        previousLabel.focus();
        previousLabel.querySelector('input').click();
    } else {
        let lastIndex = labels.length - 2;
        if (lastIndex >= 0) {
            labels[lastIndex].focus();
            labels[lastIndex].querySelector('input').click();
        }
    }
}


function trySelectNextQueueEntry() {
    const fieldset = document.querySelector('fieldset.mcww-queue-radio');
    if (!uiElementIsVisible(fieldset)) {
        return;
    }
    const labels = fieldset.querySelectorAll('label');
    if (!labels) {
        return;
    }

    const nextLabel = getNextLabel(labels);

    if (nextLabel && !nextLabel.matches('.mcww-hidden')) {
        nextLabel.focus();
        nextLabel.querySelector('input').click();
    } else {
        labels[0].focus();
        labels[0].querySelector('input').click();
    }
}


function scrollToPreviousQueueEntry() {
    const labels = document.querySelectorAll('fieldset.mcww-queue-radio label');
    if (!labels) return;
    const previousLabel = getPreviousLabel(labels);
    if (previousLabel) {
        previousLabel.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
        });
    } else {
        document.querySelector('fieldset.mcww-queue-radio label.selected')
            ?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}


function scrollToNextQueueEntry() {
    const labels = document.querySelectorAll('fieldset.mcww-queue-radio label');
    if (!labels) return;
    const nextLabel = getNextLabel(labels);
    if (nextLabel) {
        nextLabel.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
        });
    } else {
        document.querySelector('fieldset.mcww-queue-radio label.selected')
            ?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}


// temporal solution
var oldQueueIndicator = null;

async function updateQueueIndicators() {
    const response = await fetch('/mcww_api/queue_indicator');
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const indicatorValue = await response.json();
    if (oldQueueIndicator !== indicatorValue) {
        oldQueueIndicator = indicatorValue;
        TITLE.setQueueIndicator(indicatorValue);
        const indicators = document.querySelectorAll('.queue-indicator');
        indicators.forEach((indicator) => {
            if (indicatorValue) {
                indicator.classList.remove('empty-indicator');
                indicator.textContent = indicatorValue;
                if (Number.isInteger(indicatorValue)) {
                    if (indicator.textContent.length === 1 ) {
                        indicator.style.fontSize = '14px';
                    } else if (indicator.textContent.length === 2) {
                        indicator.style.fontSize = '12.3px';
                    } else {
                        indicator.style.fontSize = '10.3px';
                    }
                } else {
                    indicator.style.fontSize = '11px';
                }
            } else {
                indicator.classList.add('empty-indicator');
                indicator.textContent = "";
            }
        });
    }
}

onUiLoaded(() => {setInterval(updateQueueIndicators, 1000)});


var queueEntrySelectedFirstTime = true;

function afterQueueEntrySelected() {
    if (queueEntrySelectedFirstTime) {
        const radio = document.querySelector('fieldset.mcww-queue-radio');
        scrollSelectedIntoView(radio);
        queueEntrySelectedFirstTime = false;
    } else {
        scrollSelectedOnChange();
    }
    const selectedId = document.querySelector('fieldset.mcww-queue-radio label.selected .mcww-id');
    setSessionStorageVariable("queueLastEntrySelected", selectedId.textContent);
}


onWorkflowRendered((workflowUIParent) => {
    const workflowName = workflowUIParent?.querySelector(".queue-workflow-name span p");
    if (workflowName) {
        TITLE.setSelectedQueueWorkflow(workflowName.textContent);
    }
});


onUiLoaded(() => {
    if (getSelectedMainUIPageFromUrl() === "queue") {
        const lastId = getSessionStorageVariable("queueLastEntrySelected");
        if (!lastId) return;
        const idSelector = 'fieldset.mcww-queue-radio label .mcww-id';
        waitForElement(idSelector, () => {
            const ids = document.querySelectorAll(idSelector);
            for (const id of ids) {
                if (id.textContent === lastId) {
                    id.closest("fieldset.mcww-queue-radio label").click();
                    return;
                }
            }
        });
    }
});
