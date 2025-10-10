
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  document.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  }, false);
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

var webUIBrokenState = false;

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


///////    footer

function rebuildFooter() {
    const footer = document.querySelector('footer');
    if (!footer) {
        console.error("Footer element not found.");
        return;
    }

    const originalLinkTemplate = footer.querySelector('a.built-with');
    const originalDividerTemplate = footer.querySelector('div.divider');

    if (!originalLinkTemplate || !originalDividerTemplate) {
        console.error("Failed to find original template elements (a.built-with or div.divider) for copying.");
        return;
    }

    const newLinks = [
        { text: "Report an issue", url: "https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI/issues" },
        { text: "MCWW", url: "https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI" },
        { text: "Gradio", url: "https://www.gradio.app/" },
        { text: "ComfyUI", url: "https://www.comfy.org/" },
        { text: "Open ComfyUI", url: COMFY_ADDRESS }
    ];

    footer.innerHTML = '';

    newLinks.forEach((linkData, index) => {
        const anchor = originalLinkTemplate.cloneNode(true);
        anchor.href = linkData.url;
        anchor.textContent = linkData.text;
        footer.appendChild(anchor);
        if (index < newLinks.length - 1) {
            const divider = originalDividerTemplate.cloneNode(true);
            footer.appendChild(divider);
        }
    });
}

waitForElement("footer", rebuildFooter);


