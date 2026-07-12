
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


var _lastMouseEvent = null;
document.addEventListener('mousemove', (e) => {
    _lastMouseEvent = e;
});

function getLastMouseEvent() {
    return _lastMouseEvent || { clientX: window.innerWidth / 2, clientY: window.innerHeight / 2 };
}

var g_isTabActive = true;
let g_lastActiveTime = Date.now();

document.addEventListener('visibilitychange', () => {
    g_isTabActive = !document.hidden;
    if (g_isTabActive) {
        g_lastActiveTime = Date.now();
    }
});

function isInsidePWA() {
    return !window.matchMedia('(display-mode: browser)').matches;
}

function scrollTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function reloadPage() {
    g_waitingForReload = true;
    window.location.reload();
}


function capitalize(string)
{
    return String(string[0]).toUpperCase() + String(string).slice(1);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function simpleChecksum(buffer) {
    const view = new Uint8Array(buffer);
    let hash = 0x811c9dc5;
    for (let i = 0; i < view.length; i++) {
        hash ^= view[i];
        hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
    }
    return (hash >>> 0).toString(16).padStart(8, '0');
}

const clamp = (val, min, max) => Math.min(Math.max(val, min), max)

function isStringNumber(str) {
    return !isNaN(str) && !isNaN(parseFloat(str));
}

function removeSuffix(str, suffix) {
    if (str.endsWith(suffix)) {
        return str.slice(0, -suffix.length);
    }
    return str;
}

const truncateMiddle = (str, limit = 20, suffixLen = 5) => {
    if (str.length <= limit) {
        return str;
    }
    const edge = limit - suffixLen - 3;
    const prefixIndex = Math.max(edge, 0);
    return str.slice(0, prefixIndex) + "..." + str.slice(-suffixLen);
};


function setBrowserStorageVariable(variableName, value) {
    try {
        value = JSON.stringify(value);
        localStorage.setItem(`${MCWW.STORAGE_KEY}_${variableName}`, value);
        return true;
    } catch (error) {
        console.warn('Error setting variable in localStorage:', error);
        return false;
    }
}

function getBrowserStorageVariable(variableName, defaultValue=null) {
    try {
        const value = localStorage.getItem(`${MCWW.STORAGE_KEY}_${variableName}`);
        return value ? JSON.parse(value) : defaultValue;
    } catch (error) {
        console.warn('Error getting variable from localStorage:', error);
        return defaultValue;
    }
}

function setSessionStorageVariable(variableName, value) {
    try {
        value = JSON.stringify(value);
        sessionStorage.setItem(variableName, value);
        return true;
    } catch (error) {
        console.warn('Error setting variable in sessionStorage:', error);
        return false;
    }
}

function getSessionStorageVariable(variableName, defaultValue=null) {
    try {
        const value = sessionStorage.getItem(variableName);
        return value ? JSON.parse(value) : defaultValue;
    } catch (error) {
        console.warn('Error getting variable from sessionStorage:', error);
        return defaultValue;
    }
}


function setUrlParameter(key, value) {
    var url = new URL(window.location.href);
    url.searchParams.set(key, value);
    replaceState(null, url.href);
}

function deleteUrlParameter(key) {
    var url = new URL(window.location.href);
    url.searchParams.delete(key);
    replaceState(null, url.href);
}

function getUrlParameter(key) {
    var url = new URL(window.location.href);
    return url.searchParams.get(key);
}

function buildLocalLink(port) {
    const protocol = window.location.protocol.replace(":", "");
    let hostname = window.location.hostname;
    if (hostname.includes(":")) hostname = `[${hostname}]`;
    return `${protocol}://${hostname}:${port}`;
}

function toggleUIFullScreen() {
    if (window.matchMedia('(display-mode: fullscreen)').matches && !document.fullscreenElement) {
        grWarning("Cannot exit browser controlled fullscreen via this button.");
        return;
    }
    if (document.fullscreenElement) {
        document.exitFullscreen().catch((error) => {
            const errorText = `Error exiting fullscreen: ${error.message}`;
            grError(errorText);
            console.error(errorText, error);
        });
    } else {
        window.document.documentElement.requestFullscreen({ keyboardLock: "browser" })
            .catch((error) => {
                const errorText = `Error entering fullscreen: ${error.message}`;
                grError(errorText);
                console.error(errorText, error);
            });
    }
}

function isUIInFullscreen() {
    return window.matchMedia('(display-mode: fullscreen)').matches || document.fullscreenElement;
}


function removeTrailingQuestionMarkInUrl() {
    const url = window.location.href;
    if (url.endsWith('?') || url.includes('?#')) {
        const cleanUrl = url.replace(/\?(?=#|$)/, '');
        replaceState(null, cleanUrl);
    }
}

