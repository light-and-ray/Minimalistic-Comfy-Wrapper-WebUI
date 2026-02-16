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


class _Title {
    constructor () {
        this._baseTitle = document.title;
        this._progress = null;
        this._page = null;
        this._queueIndicator = null;
        this._selectedTab = {};
        this._selectedProjectWorkflow = null;
        this._selectedQueueWorkflow = null;
        this._mediaSessionMetadata = {
            title: null,
            artist: this._baseTitle,
            artwork: [
                {
                    "src": '/pwa/icon.png',
                    "sizes": "1024x1024",
                    "type": "image/png",
                },
            ],
        };
        this._apply();
        this.blockTitleChange = false;
    }

    setPage(value) {
        this._page = value;
        this._apply();
    }

    setTab(value) {
        this._selectedTab[this._page] = value;
        this._apply();
    }

    setProgress(value) {
        this._progress = value;
        this._apply();
    }

    setQueueIndicator(value) {
        this._queueIndicator = value;
        this._apply();
    }

    setSelectedProjectWorkflow(value) {
        this._selectedProjectWorkflow = value;
        this._apply();
    }

    setSelectedQueueWorkflow(value) {
        this._selectedQueueWorkflow = value;
        this._apply();
    }

    _apply() {
        if (this.blockTitleChange) {
            return;
        }
        if (this._page === null) {
            return;
        }
        let mediaSessionTitle = null;
        let newTitle = isInsidePWA() ? "" : this._baseTitle;
        if (this._page === "project" && this._selectedProjectWorkflow) {
            newTitle = newTitle = `${capitalize(this._selectedProjectWorkflow)} – ${newTitle}`;
            mediaSessionTitle = capitalize(this._selectedProjectWorkflow);
        } else if (this._page === "queue" && this._selectedQueueWorkflow) {
            const selectedTab = this._selectedTab[this._page];
            let pageStr = capitalize(this._page);
            pageStr = pageStr.replace(/_/g, ' ');
            newTitle = `${pageStr} – ${capitalize(this._selectedQueueWorkflow)} – ${newTitle}`;
            mediaSessionTitle = capitalize(this._selectedQueueWorkflow);
        } else {
            const selectedTab = this._selectedTab[this._page];
            if (selectedTab) {
                newTitle = `${selectedTab} – ${newTitle}`;
            } else {
                let pageStr = capitalize(this._page);
                pageStr = pageStr.replace(/_/g, ' ');
                newTitle = `${pageStr} – ${newTitle}`;
            }
            mediaSessionTitle = capitalize(this._page);
        }
        newTitle = removeSuffix(newTitle, " – ");
        if (this._progress) {
            newTitle = `${this._progress} ${newTitle}`;
        }
        if (this._queueIndicator) {
            let text = this._queueIndicator;
            if (isStringNumber(text)) {
                text = `(${text})`
            }
            newTitle = `${text} ${newTitle}`;
        }
        document.title = newTitle;
        this._mediaSessionMetadata.title = mediaSessionTitle;
        if ("mediaSession" in navigator) {
            navigator.mediaSession.metadata = new MediaMetadata(this._mediaSessionMetadata);
        }

    }
}
/** @type {_Title} */
var TITLE = null;
onUiLoaded(() => {TITLE = new _Title();});


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


function waitForElement(selector, callback, timeout = 10000) {
    const startTime = Date.now();

    function check() {
        const element = document.querySelector(selector);

        if (element) {
            callback(element);
        } else if (timeout === null || Date.now() - startTime < timeout) {
            setTimeout(check, 100);
        } else {
            console.warn(`Timeout waiting for element with selector: ${selector}`);
        }
    }

    check();
}

async function waitForElementAsync(selector, timeout = 10000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
        const element = document.querySelector(selector);
        if (element) {
            return element;
        }
        await new Promise(resolve => setTimeout(resolve, 100));
    }

    throw new Error(`Timeout waiting for element with selector: ${selector}`);
}


async function waitForElementsAsync(selectors, timeout = 10000) {
    const elements = [];
    for (const selector of selectors) {
        const element = await waitForElementAsync(selector, timeout);
        elements.push(element);
    }
    return elements;
}


var g_isTabActive = true;
let g_lastActiveTime = Date.now();


document.addEventListener('visibilitychange', () => {
    g_isTabActive = !document.hidden;
    if (g_isTabActive) {
        g_lastActiveTime = Date.now();
    }
});

onUiUpdate((updatedElements) => {
    const workflowRenderedTrigger = updatedElements.querySelectorAll('.mcww-workflow-rendered-trigger');
    if (workflowRenderedTrigger.length > 0) {
        workflowRenderedTrigger.forEach((trigger) => {
            trigger.classList.remove('mcww-workflow-rendered-trigger');
        });
        executeCallbacks(workflowRenderedCallbacks, updatedElements);
    }
});

