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


window.addEventListener('popstate', () => {
    executeCallbacks(popStateCallbacks);
});


function waitForElement(selector, callback) {
    const element = document.querySelector(selector);
    if (element) {
        callback(element);
    } else {
        setTimeout(() => waitForElement(selector, callback), 100);
    }
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


function pushState(state, url) {
    const currentState = window.history.state;
    window.history.pushState(state ?? currentState, '', url);
    executeCallbacks(stateChangedCallbacks);
}

function replaceState(state, url) {
    const currentState = window.history.state;
    window.history.replaceState(state ?? currentState, '', url);
    executeCallbacks(stateChangedCallbacks);
}

