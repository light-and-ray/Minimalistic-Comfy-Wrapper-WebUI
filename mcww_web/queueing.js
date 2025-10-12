
function onQueueButtonPressed() {
    const checkbox = document.querySelector('.queue-checkbox input[type="checkbox"]');

    if (!checkbox) {
        console.error('Checkbox not found!');
        return;
    }

    checkbox.checked = !checkbox.checked;

    const event = new Event('input', { bubbles: true });
    checkbox.dispatchEvent(event);

    const queueElement = document.querySelector('.mcww-queue');

    if (!queueElement) {
        console.error('Queue element not found!');
        return;
    }

    if (checkbox.checked) {
        queueElement.classList.add('active');
    } else {
        queueElement.classList.remove('active');
    }
}

function ensureQueueIsUnselected() {
    const queueElement = document.querySelector('.mcww-queue');
    if (!queueElement) {
        console.error('Queue element not found!');
        return;
    }
    if (queueElement.classList.contains('active')) {
        onQueueButtonPressed();
    }
}

