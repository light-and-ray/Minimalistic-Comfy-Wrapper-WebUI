
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    document.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
    }, false);
});

function goBack() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        grInfo("No history to go back to.");
        ensureProjectIsSelected();
    }
}

window.addEventListener('popstate', () => {
    selectPageFromURLArgs();
    globalExitFullscreenIfExists();
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
            grError("Backend restarted, please reload the page");
            setInterval(() => {
                grError("Backend restarted, please reload the page");
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
}

waitForElement("footer", rebuildFooter);


///////    see selected

// Store references to observed elements to detect disappearance/reappearance
const observedElements = new WeakSet();

function setupObserver() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    // Check if the added node or its children have the target class
                    const newElements = node.querySelectorAll('.need-see-selected');
                    newElements.forEach((el) => {
                        if (!observedElements.has(el)) {
                            observedElements.add(el);
                            scrollSelectedIntoView(el);
                        }
                    });
                }
            });

            // Check for removed nodes to detect disappearance
            mutation.removedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const removedElements = node.querySelectorAll('.need-see-selected');
                    removedElements.forEach((el) => {
                        observedElements.delete(el);
                    });
                }
            });
        });
    });

    // Start observing the document
    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });

    // Initial check for existing elements
    document.querySelectorAll('.need-see-selected').forEach((el) => {
        observedElements.add(el);
        scrollSelectedIntoView(el);
    });
}

function scrollSelectedIntoView(element) {
    const selected = element.querySelector('.selected');
    if (selected) {
        selected.scrollIntoView({
            block: 'center',
        });
    }
}

// Start the observer
setupObserver();
