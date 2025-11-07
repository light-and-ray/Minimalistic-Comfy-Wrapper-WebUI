// files in root of mcww_web have priority

var uiUpdateCallbacks = [];
var uiLoadedCallbacks = [];
var popStateCallbacks = [];


function onUiUpdate(callback) {
    uiUpdateCallbacks.push(callback);
}

function onUiLoaded(callback) {
    uiLoadedCallbacks.push(callback);
}

function onPopState(callback) {
    popStateCallbacks.push(callback);
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


//////////////


function dispatchGradioEvent(type, data) {
    const event = new CustomEvent("gradio", {
        detail: {
            event: type,
            data: data,
        }
    });
    document.querySelector('.gradio-container').dispatchEvent(event);
}

function grWarning(message) {
    dispatchGradioEvent("warning", message);
}

function grError(message) {
    dispatchGradioEvent("error", message);
}

function grInfo(message) {
    dispatchGradioEvent("info", message);
}


function waitForElement(selector, callback) {
    const element = document.querySelector(selector);
    if (element) {
        callback(element);
    } else {
        setTimeout(() => waitForElement(selector, callback), 100);
    }
}

function buildLocalLink(port) {
    const protocol = window.location.protocol.replace(":", "");
    let hostname = window.location.hostname;
    if (hostname.includes(":")) hostname = `[${hostname}]`;
    return `${protocol}://${hostname}:${port}`;
}


function scrollTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}


function isImageUrl(url) {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.heif', '.heic', '.jxl'];
    return imageExtensions.some(ext => url.endsWith(ext));
}


function isVideoUrl(url) {
    const videoExtensions = ['.mp4', '.webm'];
    return videoExtensions.some(ext => url.endsWith(ext));
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


function reloadPage() {
    window.location.reload();
}

function goBack() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        grInfo("No history to go back to.");
        ensureProjectIsSelected();
    }
}

