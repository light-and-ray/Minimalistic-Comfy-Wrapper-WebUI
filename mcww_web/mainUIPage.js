
function getSelectedMainUIPage() {
    return document.querySelector('.mcww-main-ui-page label.selected span')?.textContent.trim();
}


function selectMainUIPage(page) {
    if (getSelectedMainUIPage() !== page) {
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
    }

    const queueButton = document.querySelector('.mcww-queue');
    if (page === "queue") {
        queueButton.classList.add('active');
    } else {
        queueButton.classList.remove('active');
    }

    const helpersButton = document.querySelector('.mcww-helpers-button');
    if (page === "helpers") {
        helpersButton.classList.add('active');
    } else {
        helpersButton.classList.remove('active');
    }

    const settingsButton = document.querySelector('.mcww-settings-button');
    if (page === "settings") {
        settingsButton.classList.add('active');
    } else {
        settingsButton.classList.remove('active');
    }

    const url = new URL(window.location.href);
    const urlParams = new URLSearchParams(window.location.search);
    const oldPageFromURL = urlParams.get('page_') || 'project';
    if (page !== oldPageFromURL) {
        if (page !== "project") {
            url.searchParams.set('page_', page);
        } else {
            url.searchParams.delete('page_');
        }
        window.history.pushState({}, '', url.toString());
    }
}

function selectPageFromURLArgs() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page_') || 'project';
    selectMainUIPage(page);
}

function deleteCompareIfExists() {
    const url = new URL(window.location.href);
    if (url.searchParams.has('page_') && url.searchParams.get('page_') === 'compare') {
        url.searchParams.delete('page_');
        window.history.replaceState({}, '', url);
    }
}

window.addEventListener('popstate', selectPageFromURLArgs);
onUiLoaded(() => {
    deleteCompareIfExists();
    selectPageFromURLArgs();
});


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

function onHelpersButtonPressed() {
    if (getSelectedMainUIPage() === "helpers") {
        selectMainUIPage("project");
    } else {
        selectMainUIPage("helpers");
    }
}

function onSettingsButtonPressed() {
    if (getSelectedMainUIPage() === "settings") {
        selectMainUIPage("project");
    } else {
        selectMainUIPage("settings");
    }
}


