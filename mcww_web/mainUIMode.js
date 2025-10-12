
function getSelectedMainUIMode() {
    return document.querySelector('.mcww-main-ui-mode label.selected span')?.textContent.trim();
}


function selectMainUIMode(mode) {
    if (getSelectedMainUIMode() === mode) return;

    const container = document.querySelector('.mcww-main-ui-mode');
    if (!container) {
        console.error('Container ".mcww-main-ui-mode" not found.');
        return;
    }

    const labels = container.querySelectorAll('label');
    if (labels.length === 0) {
        console.error('No labels found inside ".mcww-main-ui-mode".');
        return;
    }

    let found = false;
    labels.forEach(label => {
        const span = label.querySelector('span');
        if (span && span.textContent.trim() === mode) {
            const input = label.querySelector('input');
            if (input) {
                input.click();
                found = true;
            }
        }
    });

    if (!found) {
        console.error(`No label with span containing "${mode}" found.`);
    }

    const queueButton = document.querySelector('.mcww-queue');
    if (mode === "queue") {
        queueButton.classList.add('active');
    } else {
        queueButton.classList.remove('active');
    }
}


function onQueueButtonPressed() {
    if (getSelectedMainUIMode() === "queue") {
        selectMainUIMode("project");
    } else {
        selectMainUIMode("queue");
    }
}

function ensureProjectIsSelected() {
    selectMainUIMode("project");
}

