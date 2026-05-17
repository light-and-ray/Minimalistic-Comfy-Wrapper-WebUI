// files in root of mcww_web have priority

var uiUpdateCallbacks = [];
var uiLoadedCallbacks = [];
var popStateCallbacks = [];
var pushStateCallbacks = [];
var stateChangedCallbacks = [];
var pageSelectedCallbacks = [];
var workflowRenderedCallbacks = [];


function onUiUpdate(callback) {
    uiUpdateCallbacks.push(callback);
}

function onUiLoaded(callback) {
    uiLoadedCallbacks.push(callback);
}

function onPopState(callback) {
    popStateCallbacks.push(callback);
}

function onPushState(callback) {
    pushStateCallbacks.push(callback);
}

function onStateChanged(callback) {
    stateChangedCallbacks.push(callback);
}

function onPageSelected(callback) {
    pageSelectedCallbacks.push(callback);
}

function onWorkflowRendered(callback) {
    workflowRenderedCallbacks.push(callback);
}


function executeCallbacks(callbacks, ...args) {
    for (const callback of callbacks) {
        try {
            callback(...args);
        } catch (e) {
            console.error("error running callback", callback, ":", e);
        }
    }
}

var _executedUiLoadedCallbacks = false;

function executeUiLoadedCallbacks() {
    executeCallbacks(uiLoadedCallbacks);
    _executedUiLoadedCallbacks = true;
}

var uiUpdatesMutationObserver = new MutationObserver(function(mutations) {
    if (!_executedUiLoadedCallbacks) {
        return;
    }
    let updatedElements = new UiUpdatedArray();
    let removedElements = new UiUpdatedArray();
    mutations.forEach((mutation) => {
        // Handle added nodes
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                updatedElements.push(node);
            }
        });
        // Handle removed nodes
        mutation.removedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                removedElements.push(node);
            }
        });
        // Handle attribute changes
        if (mutation.type === 'attributes') {
            updatedElements.push(mutation.target);
        }
        // Handle text content changes (characterData)
        if (mutation.type === 'characterData') {
            return;
        }
        // Handle subtree changes (e.g., childList changes in descendants)
        if (mutation.type === 'childList' && mutation.target.nodeType === Node.ELEMENT_NODE) {
            updatedElements.push(mutation.target);
        }
    });
    const removedSet = new Set(removedElements);
    updatedElements = updatedElements.filter(element => !removedSet.has(element));
    executeCallbacks(uiUpdateCallbacks, updatedElements, removedElements);
});
uiUpdatesMutationObserver.observe(document, {childList: true, subtree: true});


function waitForElement(root, selector, callback, timeout = 10001) {
    const startTime = Date.now();

    function check() {
        const element = root.querySelector(selector);

        if (element) {
            callback(element);
        } else if (timeout === null || Date.now() - startTime < timeout) {
            setTimeout(check, 100);
        } else {
            if (timeout === 10001) {
                console.warn(`Timeout waiting for element with selector: ${selector}`);
            }
        }
    }

    check();
}

async function waitForElementAsync(root, selector, timeout = 10000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
        const element = root.querySelector(selector);
        if (element) {
            return element;
        }
        await new Promise(resolve => setTimeout(resolve, 100));
    }

    throw new Error(`Timeout waiting for element with selector: ${selector}`);
}

async function waitForElementsAsync(root, selectors, timeout = 10000) {
    const elements = [];
    for (const selector of selectors) {
        const element = await waitForElementAsync(root, selector, timeout);
        elements.push(element);
    }
    return elements;
}


onUiUpdate((updatedElements) => {
    const workflowRenderedTriggers = updatedElements.querySelectorAll('.mcww-workflow-rendered-trigger');
    workflowRenderedTriggers.forEach((trigger) => {
        trigger.classList.remove('mcww-workflow-rendered-trigger');
        const workflowUI = trigger.closest(".workflow-ui");
        const workflowUIParent = workflowUI?.closest(".workflow-ui-parent");
        executeCallbacks(workflowRenderedCallbacks, workflowUIParent);
    });
});


/** @type {_Title} */
var TITLE = null;
onUiLoaded(() => {TITLE = new _Title();});
