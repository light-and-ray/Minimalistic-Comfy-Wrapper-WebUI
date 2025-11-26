
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
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.heif', '.heic', '.jxl'];
    return imageExtensions.some(ext => url.endsWith(ext));
}


function isVideoUrl(url) {
    const videoExtensions = ['.mp4', '.webm'];
    return videoExtensions.some(ext => url.endsWith(ext));
}


function getBasename(url) {
    return url.substring(url.lastIndexOf('/') + 1);
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


function removeImageExtension(string) {
    const extensions = [
        ".jpg", ".jpeg", ".webp", ".png", ".gif", ".tiff", ".tif",
        ".bmp", ".svg", ".ico", ".heif", ".heic", ".avif"
    ];

    const lowerCaseString = string.toLowerCase();

    for (const ext of extensions) {
        if (lowerCaseString.endsWith(ext)) {
            const extLength = ext.length;
            return string.slice(0, -extLength);
        }
    }
    return string;
}


function setBrowserStorageVariable(variableName, variable) {
    try {
        const value = JSON.stringify(variable);
        localStorage.setItem(`${STORAGE_KEY}_${variableName}`, value);
        return true;
    } catch (error) {
        console.error('Error setting variable in localStorage:', error);
        return false;
    }
}

function getBrowserStorageVariable(variableName) {
    try {
        const value = localStorage.getItem(`${STORAGE_KEY}_${variableName}`);
        return value ? JSON.parse(value) : null;
    } catch (error) {
        console.error('Error getting variable from localStorage:', error);
        return null;
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
