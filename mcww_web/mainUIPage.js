
function getSelectedMainUIPage() {
    return document.querySelector('.mcww-main-ui-page label.selected span')?.textContent.trim();
}


function selectMainUIPage(page) {
    if (getSelectedMainUIPage() === page) return;

    const container = document.querySelector('.mcww-main-ui-page');
    if (!container) {
        console.error('Container ".mcww-main-ui-page" not found.');
        return;
    }

    const labels = container.querySelectorAll('label');
    if (labels.length === 0) {
        console.error('No labels found inside ".mcww-main-ui-page".');
        return;
    }

    let found = false;
    labels.forEach(label => {
        const span = label.querySelector('span');
        if (span && span.textContent.trim() === page) {
            const input = label.querySelector('input');
            if (input) {
                input.click();
                found = true;
            }
        }
    });

    if (!found) {
        console.error(`No label with span containing "${page}" found.`);
    }

    const queueButton = document.querySelector('.mcww-queue');
    if (page === "queue") {
        queueButton.classList.add('active');
    } else {
        queueButton.classList.remove('active');
    }
}


function onQueueButtonPressed() {
    if (getSelectedMainUIPage() === "queue") {
        selectMainUIPage("project");
    } else {
        selectMainUIPage("queue");
    }
}

function ensureProjectIsSelected() {
    selectMainUIPage("project");
}

