
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

waitForElement('.mcww-queue', addSvgToMcwwQueue)
