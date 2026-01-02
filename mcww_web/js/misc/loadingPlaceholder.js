
function activateLoadingPlaceholder() {
    let activeWorkflowUI = document.querySelector(".active-workflow-ui");
    let workflowLoadingPlaceholder = document.querySelector(".workflow-loading-placeholder");
    if (activeWorkflowUI && workflowLoadingPlaceholder) {
        activeWorkflowUI.classList.add("mcww-hidden");
        workflowLoadingPlaceholder.classList.remove("mcww-hidden");
    }
}

function removeStartupLoader() {
    const loadingElements = document.querySelectorAll('.startup-loading');
    loadingElements.forEach((loadingElement) => {
        loadingElement.parentElement.parentElement.parentElement.remove();
    });
}

