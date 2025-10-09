
window.addEventListener('beforeunload', (event) => {
    event.preventDefault();
    event.returnValue = "Are you sure?";
});


[...document.getElementsByClassName('cm-content')].forEach(elem => elem.setAttribute('spellcheck', 'true'));


///////    loading

function activateLoadingPlaceholder(...args) {
    let activeWorkflowUI = document.querySelector(".active-workflow-ui");
    let workflowLoadingPlaceholder = document.querySelector(".workflow-loading-placeholder");
    if (activeWorkflowUI && workflowLoadingPlaceholder) {
        activeWorkflowUI.classList.add("mcww-hidden");
        workflowLoadingPlaceholder.classList.remove("mcww-hidden");
    }
}

waitForElement('.active-workflow-ui', () => {
    const loadingElement = document.querySelector('.startup-loading');
    if (loadingElement) {
        loadingElement.parentElement.parentElement.parentElement.remove();
    }
});


///////    backend checks

let webUIBrokenState = false;

async function ensureSameAppId() {
    try {
        if (webUIBrokenState) {
            return;
        }
        const response = await fetch('/config');
        if (!response.ok) {
            grWarning("Backend is not available");
            return;
        }

        const config = await response.json();

        if (window.gradio_config.app_id !== config.app_id) {
            grError("Backend restarted, please reload the page");
            setInterval(() => {
                grError("Backend restarted, please reload the page");
            }, 10000);
            webUIBrokenState = true;
        }
    } catch (error) {
        grWarning("Backend is not available");
    }
}
setInterval(ensureSameAppId, 5100);


///////    sidebar

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
