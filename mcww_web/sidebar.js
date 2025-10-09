
const sidebarCloseButtonSelector = '.sidebar.open .toggle-button';

function hideSidebarOnMobile() {
    if (window.innerWidth < 768) {
        const closeButton = document.querySelector(sidebarCloseButtonSelector);
        if (closeButton) {
            closeButton.click();
        }
    }
}

waitForElement(sidebarCloseButtonSelector, hideSidebarOnMobile);


function addCloseButtons() {
    const fieldset = document.querySelector('.projects-radio');
    if (!fieldset) {
        console.error("Fieldset with class '.projects-radio' not found.");
        return;
    }
    const labels = fieldset.querySelectorAll('label');
    labels.forEach((label, index) => {
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

function closeProject(n) {
    grInfo(`Closing project at index: ${n}`);
}

waitForElement('.projects-radio label', addCloseButtons);

