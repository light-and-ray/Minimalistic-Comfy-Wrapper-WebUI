// files in root of mcww_web have priority

var uiUpdateCallbacks = [];
var uiLoadedCallbacks = [];
var popStateCallbacks = [];
var stateChangedCallbacks = [];
var pageSelectedCallbacks = [];


function onUiUpdate(callback) {
    uiUpdateCallbacks.push(callback);
}

function onUiLoaded(callback) {
    uiLoadedCallbacks.push(callback);
}

function onPopState(callback) {
    popStateCallbacks.push(callback);
}

function onStateChanged(callback) {
    stateChangedCallbacks.push(callback);
}

function onPageSelected(callback) {
    pageSelectedCallbacks.push(callback);
}


class _Title {
    constructor () {
        this._baseTitle = document.title;
        this._progress = null;
        this._page = null;
        this._queueIndicator = null;
        this._selectedTab = {};
        this._selectedWorkflow = null;
        this._apply();
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

    setSelectedWorkflow(value) {
        this._selectedWorkflow = value;
        this._apply();
    }

    _apply() {
        let newTitle = this._baseTitle;
        if (this._page) {
            const selectedTab = this._selectedTab[this._page];
            if (selectedTab) {
                newTitle = `${selectedTab} – ${newTitle}`;
            } else {
                newTitle = `${capitalize(this._page)} – ${newTitle}`;
            }
        } else if (this._selectedWorkflow) {
            newTitle = newTitle = `${capitalize(this._selectedWorkflow)} – ${newTitle}`;
        }
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
    }
}
/** @type {_Title} */
var TITLE = null;
onUiLoaded(() => {TITLE = new _Title();});


function executeCallbacks(queue, arg) {
    for (const callback of queue) {
        try {
            callback(arg);
        } catch (e) {
            console.error("error running callback", callback, ":", e);
        }
    }
}


var executedOnLoaded = false;

var mutationObserver = new MutationObserver(function(m) {
    if (!executedOnLoaded && document.querySelector('.active-workflow-ui')) {
        executedOnLoaded = true;
        executeCallbacks(uiLoadedCallbacks);
    }

    executeCallbacks(uiUpdateCallbacks, m);
});
mutationObserver.observe(document, {childList: true, subtree: true});


function waitForElement(selector, callback, timeout = 10000) {
    const startTime = Date.now();

    function check() {
        const element = document.querySelector(selector);

        if (element) {
            callback(element);
        } else if (Date.now() - startTime < timeout) {
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


['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    document.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
    }, false);
});


var g_isTabActive = true;
let g_lastActiveTime = Date.now();

const handleVisibilityChange = () => {
    g_isTabActive = !document.hidden;
    if (g_isTabActive) {
        g_lastActiveTime = Date.now();
    }
};

document.addEventListener('visibilitychange', handleVisibilityChange);


let isBackNavigationInProgress = false;
const pendingStateQueue = [];

function goBack() {
    if (window.history.length > 1) {
        isBackNavigationInProgress = true;
        window.history.back();
    } else {
        grInfo("No history to go back to.");
        ensureProjectIsSelected();
    }
}

window.addEventListener('popstate', () => {
    isBackNavigationInProgress = false;

    while (pendingStateQueue.length > 0) {
        const task = pendingStateQueue.shift();

        if (task.type === 'push') {
            pushState(task.state, task.url);
        } else if (task.type === 'replace') {
            replaceState(task.state, task.url);
        }
    }

    executeCallbacks(popStateCallbacks);
    executeCallbacks(stateChangedCallbacks);
});

function pushState(state, url) {
    if (isBackNavigationInProgress) {
        pendingStateQueue.push({ type: 'push', state, url });
        return;
    }

    const currentState = window.history.state;
    window.history.pushState(state ?? currentState, '', url);
    executeCallbacks(stateChangedCallbacks);
}

function replaceState(state, url) {
    if (isBackNavigationInProgress) {
        pendingStateQueue.push({ type: 'replace', state, url });
        return;
    }

    const currentState = window.history.state;
    window.history.replaceState(state ?? currentState, '', url);
    executeCallbacks(stateChangedCallbacks);
}

