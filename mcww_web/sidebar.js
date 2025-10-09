
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
