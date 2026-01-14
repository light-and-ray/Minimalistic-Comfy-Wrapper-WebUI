const getHistoryDepth = () => parseInt(sessionStorage.getItem('appHistoryDepth') || '0', 10);
const setHistoryDepth = (val) => sessionStorage.setItem('appHistoryDepth', val.toString());

onPopState(() => {
    setHistoryDepth(Math.max(getHistoryDepth() - 1, 0));
});

onPushState(() => {
    setHistoryDepth(getHistoryDepth() + 1);
});


let isBackNavigationInProgress = false;
const pendingStateQueue = [];

function goBack() {
    if (getHistoryDepth() > 1) {
        isBackNavigationInProgress = true;
        window.history.back();
    } else {
        console.warn("No history to go back to.");
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
    executeCallbacks(pushStateCallbacks);
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
