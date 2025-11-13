
const sidebarCloseButtonSelector = '.sidebar.open .toggle-button';

function closeSidebarOnMobile() {
    if (window.innerWidth <= 768) {
        const closeButton = document.querySelector(sidebarCloseButtonSelector);
        if (closeButton) {
            closeButton.click();
        }
    }
}

waitForElement(sidebarCloseButtonSelector, closeSidebarOnMobile);


function addCloseButtons() {
    const fieldset = document.querySelector('.projects-radio');
    if (!fieldset) {
        console.error("Fieldset with class '.projects-radio' not found.");
        return;
    }
    const labels = fieldset.querySelectorAll('label');
    labels.forEach((label, index) => {
        if (label.querySelector('.close-project-btn')) {
            return;
        }
        const closeButton = document.createElement('button');
        closeButton.setAttribute('type', 'button');
        closeButton.classList.add('close-project-btn');
        closeButton.innerHTML = '×';

        closeButton.addEventListener('click', (event) => {
            event.stopPropagation();
            event.preventDefault();
            closeProject(index);
        });

        label.appendChild(closeButton);
    });
}

waitForElement('.projects-radio', ()=>{onUiUpdate(addCloseButtons)});


function closeProject(n) {
    const fieldset = document.querySelector('.close-projects-radio');
    if (!fieldset) {
        console.error("Fieldset with class '.close-projects-radio' not found.");
        return;
    }
    const radioButtons = fieldset.querySelectorAll('input[type="radio"]');

    if (n >= 0 && n < radioButtons.length) {
        const targetRadioButton = radioButtons[n];
        targetRadioButton.click();
    } else {
        console.warn(`Invalid project number 'n': ${n}. Radio button not found.`);
    }
}


function addLogoClick() {
    const logo = document.querySelector('.mcww-logo');
    if (logo) {
        logo.addEventListener('click', () => {
            closeSidebarOnMobile();
            scrollTop();
        });
    } else {
        console.error('Element with class ".mcww-logo" not found.');
    }
}

waitForElement(".mcww-logo", addLogoClick);


function addSvgToMcwwQueue() {
    const mcwwQueue = document.querySelector('.mcww-queue');

    if (mcwwQueue) {
        svgString = QUEUE_SVG_ICON;

        mcwwQueue.insertAdjacentHTML('afterbegin', svgString);
    } else {
        console.error('Could not find .mcww-queue component');
    }
}

waitForElement('.mcww-queue', addSvgToMcwwQueue);


function addSelectedProjectClick() {
    const label = document.querySelector('.projects-radio label.selected');

    if (label) {
        if (!label.dataset.clickAttached) {
            label.addEventListener('click', () => {
                closeSidebarOnMobile();
                ensureProjectIsSelected();
            })
            label.dataset.clickAttached = 'true';
        }
    }
}

onUiUpdate(addSelectedProjectClick);


// buttons


onPageSelected((page) => {
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

    const optionsButton = document.querySelector('.mcww-options-button');
    if (page === "options") {
        optionsButton.classList.add('active');
    } else {
        optionsButton.classList.remove('active');
    }

});


function onQueueButtonPressed() {
    if (getSelectedMainUIPage() === "queue") {
        goBack();
    } else {
        selectMainUIPage("queue");
    }
}

function ensureProjectIsSelected() {
    if (getSelectedMainUIPage() !== "project") {
        selectMainUIPage("project");
    }
}

function onHelpersButtonPressed() {
    if (getSelectedMainUIPage() === "helpers") {
        goBack();
    } else {
        selectMainUIPage("helpers");
    }
}

function onOptionsButtonPressed() {
    if (getSelectedMainUIPage() === "options") {
        goBack();
    } else {
        selectMainUIPage("options");
    }
}


function attachAnchors() {
    const selectors = [
        { selector: ".mcww-helpers-button", page: "helpers" },
        { selector: ".mcww-options-button", page: "options" },
        { selector: ".mcww-queue", page: "queue" }
    ];

    selectors.forEach(({ selector, page }) => {
        const button = document.querySelector(selector);
        if (button) {
            const anchor = document.createElement("a");
            anchor.href = getUrlForNewPage(page);
            button.parentNode.insertBefore(anchor, button);
            anchor.appendChild(button);
            anchor.classList = button.classList;
            button.classList = [];
            anchor.addEventListener("click", function(e) {
                if (!e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey) {
                    e.preventDefault();
                } else {
                    e.stopImmediatePropagation();
                }
            }, true);
            onStateChanged(() => {
                anchor.href = getUrlForNewPage(page);
            });
        }
    });
}

onUiLoaded(attachAnchors);

