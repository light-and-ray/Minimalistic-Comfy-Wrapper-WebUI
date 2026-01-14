
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
    const lowerCaseUrl = url.toLowerCase();
    return IMAGE_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}


function isVideoUrl(url) {
    const lowerCaseUrl = url.toLowerCase();
    return VIDEO_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}


function getBasename(url) {
    return url.substring(url.lastIndexOf('/') + 1);
}


function removeImageExtension(string) {
    const lowerCaseString = string.toLowerCase();

    for (const ext of IMAGE_EXTENSIONS) {
        if (lowerCaseString.endsWith(ext)) {
            const extLength = ext.length;
            return string.slice(0, -extLength);
        }
    }
    return string;
}


function getShortImageName(url) {
    return removeImageExtension(getBasename(decodeURIComponent(url))).slice(0, 50)
}


function capitalize(string)
{
    return String(string[0]).toUpperCase() + String(string).slice(1);
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


function reloadPage() {
    window.location.reload();
}


function uiElementIsVisible(element) {
    if (!element) {
        return false;
    }
    if (element === document) {
        return true;
    }

    const computedStyle = getComputedStyle(element);
    const isVisible = computedStyle.display !== 'none';

    if (!isVisible) return false;
    return uiElementIsVisible(element.parentNode);
}


function uiElementInSight(el) {
    const clRect = el.getBoundingClientRect();
    const windowHeight = window.innerHeight;
    const isOnScreen = clRect.bottom > 0 && clRect.top < windowHeight;

    return isOnScreen;
}

var _lastMouseEvent = null;
document.addEventListener('mousemove', (e) => {
    _lastMouseEvent = e;
});

function getLastMouseEvent() {
    return _lastMouseEvent || { clientX: window.innerWidth / 2, clientY: window.innerHeight / 2 };
}


function tryModifySlider(difference, selector) {
    const slider = document.querySelector(selector);
    if (!slider) return;
    const currentValue = parseFloat(slider.value);
    const minValue = parseFloat(slider.min);
    const maxValue = parseFloat(slider.max);
    let newValue = currentValue + difference;
    if (newValue < minValue) newValue = minValue;
    if (newValue > maxValue) newValue = maxValue;
    slider.value = newValue;
    const event = new Event('input', {
        bubbles: true,
        cancelable: true,
    });
    slider.dispatchEvent(event);
}


function setBrowserStorageVariable(variableName, variable) {
    try {
        const value = JSON.stringify(variable);
        localStorage.setItem(`${STORAGE_KEY}_${variableName}`, value);
        return true;
    } catch (error) {
        console.warn('Error setting variable in localStorage:', error);
        return false;
    }
}

function getBrowserStorageVariable(variableName, defaultValue=null) {
    try {
        const value = localStorage.getItem(`${STORAGE_KEY}_${variableName}`);
        return value ? JSON.parse(value) : defaultValue;
    } catch (error) {
        console.warn('Error getting variable from localStorage:', error);
        return defaultValue;
    }
}


function imgUrlToFile(imgUrl) {
    return new Promise((resolve, reject) => {
        try {
            const img = document.createElement('img');
            img.src = imgUrl;
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                ctx.drawImage(img, 0, 0);
                let imageName = getBasename(img.src);
                imageName = removeImageExtension(imageName) + ".png";
                canvas.toBlob((blob) => {
                    try {
                        const file = new File([blob], imageName, { type: "image/png" });
                        resolve(file);
                    } catch (error) {
                        console.error("Failed on imgUrlToFile:", error);
                        reject(error);
                    }
                }, 'image/png');
            };
            img.onerror = (error) => {
                console.error("Failed to load image:", error);
                reject(error);
            };
        } catch (error) {
            console.error("Failed on imgUrlToFile:", error);
            reject(error);
        }
    });
}


function isTabsOverflowMenuOpen() {
    const overflowMenu = document.querySelector('.overflow-dropdown');
    return (overflowMenu && uiElementIsVisible(overflowMenu))
}


function canvasToImageFile(canvas) {
    return new Promise((resolve, reject) => {
        canvas.toBlob((blob) => {
            if (blob) {
                const timestamp = new Date().getTime();
                const file = new File([blob], `tmp-${timestamp}.png`, { type: "image/png" });
                resolve(file);
            } else {
                reject(new Error("Failed to create blob from canvas."));
            }
        }, 'image/png', 1.0);
    });
}


async function awaitImageLoad(imgElement, timeout = 5000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
        if (imgElement.complete && imgElement.naturalWidth !== 0) {
            return imgElement;
        }
        await sleep(50);
    }

    throw new Error('Image loading timed out');
}


function getContentWidth(element) {
    let widthWithPaddings = element.clientWidth;
    const elementComputedStyle = window.getComputedStyle(element, null);
    return (
        widthWithPaddings - parseFloat(elementComputedStyle.paddingLeft) - parseFloat(elementComputedStyle.paddingRight)
    );
}


const clamp = (val, min, max) => Math.min(Math.max(val, min), max)


function isStringNumber(str) {
    return !isNaN(str) && !isNaN(parseFloat(str));
}


function addOnResizeCallback(container, callback) {
    const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
            callback(entry.contentRect.width, entry.contentRect.height);
        }
    });
    resizeObserver.observe(container);

    const mutationObserver = new MutationObserver((mutations) => {
        if (!document.body.contains(container)) {
            resizeObserver.disconnect();
            mutationObserver.disconnect();
        }
    });
    mutationObserver.observe(document.body, { childList: true, subtree: true });

    return resizeObserver;
}

function isScrollableTop(element) {
    while (element && element !== document.body) {
        const style = window.getComputedStyle(element);
        if (
            element.scrollHeight > element.clientHeight && element.scrollTop !== 0 &&
            (style.overflowY === 'auto' || style.overflowY === 'scroll')
        ) {
            return true;
        }
        element = element.parentElement;
    }
    return false;
}

function removeSuffix(str, suffix) {
    if (str.endsWith(suffix)) {
        return str.slice(0, -suffix.length);
    }
    return str;
}

function isInsidePWA() {
    return window.matchMedia('(display-mode: standalone)').matches;
}


function setSessionStorageVariable(variableName, variable) {
    try {
        const value = JSON.stringify(variable);
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
