
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    document.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
    }, false);
});


///////    loading

function activateLoadingPlaceholder() {
    let activeWorkflowUI = document.querySelector(".active-workflow-ui");
    let workflowLoadingPlaceholder = document.querySelector(".workflow-loading-placeholder");
    if (activeWorkflowUI && workflowLoadingPlaceholder) {
        activeWorkflowUI.classList.add("mcww-hidden");
        workflowLoadingPlaceholder.classList.remove("mcww-hidden");
    }
}

function removeStartupLoader() {
    const loadingElement = document.querySelector('.startup-loading');
    if (loadingElement) {
        loadingElement.parentElement.parentElement.parentElement.remove();
    }
}

onUiLoaded(removeStartupLoader);


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
            const errorText = "Backend restarted, please <a href=''>reload the page</a>";
            grError(errorText);
            setInterval(() => {
                grError(errorText);
            }, 10000);
            webUIBrokenState = true;
            window.fetch = () => {
                throw new Error("All connections are blocked due to broken state");
            };
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
    footer.classList.add("mcww-visible");
}

waitForElement("footer", rebuildFooter);


///////    see selected


function scrollSelectedIntoView(element) {
    const selected = element.querySelector('.selected');
    if (selected) {
        requestAnimationFrame(() => {
            selected.scrollIntoView({
                behavior: 'instant',
                block: 'center',
            });
        });
    }

}


const observedElements = new WeakSet();

onUiUpdate((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                const newElements = node.querySelectorAll('.scroll-to-selected');
                newElements.forEach((el) => {
                    if (!observedElements.has(el)) {
                        observedElements.add(el);
                        scrollSelectedIntoView(el);
                    }
                });
            }
        });
        mutation.removedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                const removedElements = node.querySelectorAll('.scroll-to-selected');
                removedElements.forEach((el) => {
                    observedElements.delete(el);
                });
            }
        });
    });
});


function scrollSelectedOnChange() {
    const selectedElements = document.querySelectorAll('.scroll-to-selected .selected');
    selectedElements.forEach((selected) => {
        selected.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
        });
    });
}


///////    mouse alert


function mouseAlert(message, duration = 350) {
    const alertElement = document.createElement('div');
    alertElement.className = 'mouse-alert';
    alertElement.textContent = message;

    const progressBar = document.createElement('div');
    progressBar.className = 'mouse-alert-progress';
    alertElement.appendChild(progressBar);

    const positionAtCursor = (e) => {
        const x = e ? e.clientX : window.innerWidth / 2;
        const y = e ? e.clientY + 57 : window.innerHeight / 2;
        alertElement.style.left = `${x}px`;
        alertElement.style.top = `${y}px`;
    };

    document.body.appendChild(alertElement);

    // Animate progress bar
    progressBar.style.transitionDuration = `${duration}ms`;
    setTimeout(() => {
        progressBar.style.transform = 'scaleX(0)';
    }, 10);

    setTimeout(() => {
        alertElement.remove();
    }, duration);

    const lastMouseEvent = window.lastMouseEvent || { clientX: window.innerWidth / 2, clientY: window.innerHeight / 2 };
    positionAtCursor(lastMouseEvent);
}

document.addEventListener('mousemove', (e) => {
    window.lastMouseEvent = e;
});

