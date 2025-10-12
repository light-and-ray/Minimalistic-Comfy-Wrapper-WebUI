
const sidebarCloseButtonSelector = '.sidebar.open .toggle-button';

function closeSidebarOnMobile() {
    if (window.innerWidth < 768) {
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


function addLogoScrollToTop() {
    const logo = document.querySelector('.mcww-logo');
    if (logo) {
        logo.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    } else {
        console.error('Element with class ".mcww-logo" not found.');
    }
}

waitForElement(".mcww-logo", addLogoScrollToTop);


function addSvgToMcwwQueue() {
    const mcwwQueue = document.querySelector('.mcww-queue');

    if (mcwwQueue) {
        svgString = `
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="256" height="256" viewBox="0 0 256 256" xml:space="preserve">
    <g style="stroke: none; stroke-width: 0; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: none; fill-rule: nonzero; opacity: 1;" transform="translate(1.4065934065934016 1.4065934065934016) scale(2.81 2.81)">
        <path d="M 48.831 86.169 c -13.336 0 -25.904 -6.506 -33.62 -17.403 c -2.333 -3.295 -4.163 -6.901 -5.437 -10.717 l 5.606 -1.872 c 1.09 3.265 2.657 6.352 4.654 9.174 c 6.61 9.336 17.376 14.908 28.797 14.908 c 19.443 0 35.26 -15.817 35.26 -35.26 c 0 -19.442 -15.817 -35.259 -35.26 -35.259 C 29.389 9.74 13.571 25.558 13.571 45 h -5.91 c 0 -22.701 18.468 -41.169 41.169 -41.169 C 71.532 3.831 90 22.299 90 45 C 90 67.701 71.532 86.169 48.831 86.169 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(0,0,0); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
        <polygon points="64.67,61.69 45.88,46.41 45.88,19.03 51.78,19.03 51.78,43.59 68.4,57.1 " style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(0,0,0); fill-rule: nonzero; opacity: 1;" transform="  matrix(1 0 0 1 0 0) "/>
        <polygon points="21.23,40.41 10.62,51.02 0,40.41 " style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(0,0,0); fill-rule: nonzero; opacity: 1;" transform="  matrix(1 0 0 1 0 0) "/>
    </g>
    </svg>
        `;

        mcwwQueue.insertAdjacentHTML('afterbegin', svgString);
    } else {
        console.error('Could not find .mcww-queue component');
    }
}

waitForElement('.mcww-queue', addSvgToMcwwQueue);


function addSelectedProjectCloseSidebarOnMobile() {
    const label = document.querySelector('.projects-radio label.selected');

    if (label) {
        if (!label.dataset.closeSidebarOnMobileAttached) {
            label.addEventListener('click', () => {
                closeSidebarOnMobile();
                ensureQueueIsUnselected();
            })
            label.dataset.closeSidebarOnMobileAttached = 'true';
        }
    }
}

onUiUpdate(addSelectedProjectCloseSidebarOnMobile);
