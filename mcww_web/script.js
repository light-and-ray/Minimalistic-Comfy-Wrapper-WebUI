function gradioApp() {
    const elems = document.getElementsByTagName('gradio-app');
    const elem = elems.length == 0 ? document : elems[0];

    if (elem !== document) {
        elem.getElementById = function(id) {
            return document.getElementById(id);
        };
    }
    return elem.shadowRoot ? elem.shadowRoot : elem;
}

var uiUpdateCallbacks = [];
var uiAfterUpdateCallbacks = [];
var uiLoadedCallbacks = [];
var optionsChangedCallbacks = [];
var optionsAvailableCallbacks = [];
var uiAfterUpdateTimeout = null;

/**
 * Register callback to be called at each UI update.
 * The callback receives an array of MutationRecords as an argument.
 */
function onUiUpdate(callback) {
    uiUpdateCallbacks.push(callback);
}

/**
 * Register callback to be called soon after UI updates.
 * The callback receives no arguments.
 *
 * This is preferred over `onUiUpdate` if you don't need
 * access to the MutationRecords, as your function will
 * not be called quite as often.
 */
function onAfterUiUpdate(callback) {
    uiAfterUpdateCallbacks.push(callback);
}

/**
 * Register callback to be called when the UI is loaded.
 * The callback receives no arguments.
 */
function onUiLoaded(callback) {
    uiLoadedCallbacks.push(callback);
}

/**
 * Register callback to be called when the options are changed.
 * The callback receives no arguments.
 * @param callback
 */
function onOptionsChanged(callback) {
    optionsChangedCallbacks.push(callback);
}

/**
 * Register callback to be called when the options (in opts global variable) are available.
 * The callback receives no arguments.
 * If you register the callback after the options are available, it's just immediately called.
 */
function onOptionsAvailable(callback) {
    if (Object.keys(opts).length != 0) {
        callback();
        return;
    }

    optionsAvailableCallbacks.push(callback);
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

/**
 * Schedule the execution of the callbacks registered with onAfterUiUpdate.
 * The callbacks are executed after a short while, unless another call to this function
 * is made before that time. IOW, the callbacks are executed only once, even
 * when there are multiple mutations observed.
 */
function scheduleAfterUiUpdateCallbacks() {
    clearTimeout(uiAfterUpdateTimeout);
    uiAfterUpdateTimeout = setTimeout(function() {
        executeCallbacks(uiAfterUpdateCallbacks);
    }, 200);
}

var executedOnLoaded = false;

var mutationObserver = new MutationObserver(function(m) {
    if (!executedOnLoaded && gradioApp().querySelector('.active-workflow-ui')) {
        executedOnLoaded = true;
        executeCallbacks(uiLoadedCallbacks);
    }

    executeCallbacks(uiUpdateCallbacks, m);
    scheduleAfterUiUpdateCallbacks();
});
mutationObserver.observe(gradioApp(), {childList: true, subtree: true});



/**
 * checks that a UI element is not in another hidden element or tab content
 */
function uiElementIsVisible(el) {
    if (el === document) {
        return true;
    }

    const computedStyle = getComputedStyle(el);
    const isVisible = computedStyle.display !== 'none';

    if (!isVisible) return false;
    return uiElementIsVisible(el.parentNode);
}

function uiElementInSight(el) {
    const clRect = el.getBoundingClientRect();
    const windowHeight = window.innerHeight;
    const isOnScreen = clRect.bottom > 0 && clRect.top < windowHeight;

    return isOnScreen;
}


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

// Save original methods
const originalScrollTo = window.scrollTo.bind(window);
const originalScrollBy = window.scrollBy.bind(window);
const originalScrollIntoView = Element.prototype.scrollIntoView;

// Override window.scrollTo
Object.defineProperty(window, 'scrollTo', {
  value: function() {
    console.warn("window.scrollTo blocked.");
    // Optionally, call the original method if needed
    // originalScrollTo(...arguments);
  },
  writable: true,
  configurable: true,
});

// Override window.scrollBy
Object.defineProperty(window, 'scrollBy', {
  value: function() {
    console.warn("window.scrollBy blocked.");
    // Optionally, call the original method if needed
    // originalScrollBy(...arguments);
  },
  writable: true,
  configurable: true,
});

// Override Element.prototype.scrollIntoView
Object.defineProperty(Element.prototype, 'scrollIntoView', {
  value: function() {
    console.warn("Element.scrollIntoView blocked.");
    // Optionally, call the original method if needed
    // originalScrollIntoView.call(this, ...arguments);
  },
  writable: true,
  configurable: true,
});


function scrollTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}
