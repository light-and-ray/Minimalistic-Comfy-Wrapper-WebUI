
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
    return MCWW.IMAGE_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}

function isVideoUrl(url) {
    const lowerCaseUrl = url.toLowerCase();
    return MCWW.VIDEO_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}

function isAudioUrl(url) {
    const lowerCaseUrl = url.toLowerCase();
    return MCWW.AUDIO_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}

function isModel3DUrl(url) {
    const lowerCaseUrl = url.toLowerCase();
    return MCWW.MODEL_3D_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}


function getBasename(url) {
    const basename = url.substring(url.lastIndexOf('/') + 1);
    return decodeURIComponent(basename);
}


function removeImageExtension(string) {
    const lowerCaseString = string.toLowerCase();

    for (const ext of MCWW.IMAGE_EXTENSIONS) {
        if (lowerCaseString.endsWith(ext)) {
            const extLength = ext.length + 1;
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


function simpleChecksum(buffer) {
    const view = new Uint8Array(buffer);
    let hash = 0x811c9dc5;
    for (let i = 0; i < view.length; i++) {
        hash ^= view[i];
        hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
    }
    return (hash >>> 0).toString(16).padStart(8, '0');
}


async function getBlobHash(blob, length = null) {
    const arrayBuffer = await blob.arrayBuffer();
    let hashHex = '';
    if (crypto?.subtle) {
        const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        hashHex = hashArray
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    } else {
        hashHex = simpleChecksum(arrayBuffer);
    }

    return length ? hashHex.slice(0, length) : hashHex;
}


async function fileUrlToFile(fileUrl) {
    try {
        const response = await fetch(fileUrl);
        if (!response.ok) throw new Error(`Failed to fetch file: ${response.statusText}`);
        let blob = await response.blob();
        let fileName;
        if (fileUrl.startsWith('blob:')) {
            let tmpBlobFileName = getSessionStorageVariable("tmpBlobFileName");
            if (tmpBlobFileName) {
                fileName = tmpBlobFileName;
            } else {
                let extension = blob.type.split('/')[1] || 'bin';
                const extensionMap = {
                    'mpeg': 'mp3',
                    'quicklime': 'mov',
                    'jpeg': 'jpg',
                    'x-msfido': 'avi',
                };
                extension = extensionMap[extension] || extension;
                fileName = `file_${await getBlobHash(blob, 20)}.${extension}`;
            }
        } else {
            fileName = getBasename(fileUrl);
        }
        if (isImageUrl(fileUrl) && !blob.type.startsWith("image/")) {
            console.log(`Image ${fileUrl} will be converted to png, because` +
                ` fetched blob doesn't have an image type`);
            blob = await convertBlobToPng(blob);
        }
        return new File([blob], fileName, { type: blob.type });
    } catch (error) {
        console.error("Failed on fileUrlToFile:", error);
        throw error;
    }
}


function isTabsOverflowMenuOpen() {
    const overflowMenus = document.querySelectorAll('.overflow-dropdown');
    return Array.from(overflowMenus).some(menu => uiElementIsVisible(menu));
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

class UiUpdatedArray extends Array {
    querySelector(selector) {
        let result = null;
        for (const item of this) {
            if (item?.matches(selector)) {
                return item;
            }
            result = item?.querySelector(selector);
            if (result) {
                return result;
            }
            const closest = item?.closest(selector);
            if (closest) {
                return closest;
            }
        }
        return result;
    }

    querySelectorAll(selector) {
        let results = [];
        for (const item of this) {
            if (item.querySelectorAll) {
                const found = item.querySelectorAll(selector);
                results.push(...found);
            }
            if (item?.matches(selector)) {
                results.push(item);
            }
            const closest = item?.closest(selector);
            if (closest) {
                results.push(closest);
            }
        }
        results = [...new Set(results)]
        return results;
    }
}


const g_cleanOnRemoveDict = new WeakMap();

function addEventListenerWithCleanup(element, type, listener, ...args) {
    element.addEventListener(type, listener, ...args);
    if (!g_cleanOnRemoveDict.has(element)) {
        g_cleanOnRemoveDict.set(element, []);
    }
    g_cleanOnRemoveDict.get(element).push(() => {
        element.removeEventListener(type, listener);
    });
}

onUiUpdate((updatedElements, removedElements) => {
    removedElements.forEach(element => {
        const targets = [element, ...element.querySelectorAll('*')];
        targets.forEach(target => {
            const cleanups = g_cleanOnRemoveDict.get(target);
            if (cleanups) {
                cleanups.forEach(cleanup => cleanup());
                g_cleanOnRemoveDict.delete(target);
            }
        });
    });
});


const truncateMiddle = (str, limit = 20, suffixLen = 5) => {
    if (str.length <= limit) {
        return str;
    }
    const edge = limit - suffixLen - 3;
    const prefixIndex = Math.max(edge, 0);
    return str.slice(0, prefixIndex) + "..." + str.slice(-suffixLen);
};


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


function getFullElementSize(element) {
    const style = window.getComputedStyle(element);
    // getBoundingClientRect() provides the width/height including scaling
    const rect = element.getBoundingClientRect();
    // Margins are never included in the bounding rect or offset sizes
    const margins = {
        width: parseFloat(style.marginLeft) + parseFloat(style.marginRight),
        height: parseFloat(style.marginTop) + parseFloat(style.marginBottom)
    };
    return {
        width: rect.width + margins.width,
        height: rect.height + margins.height
    };
}


function convertBlobToPng(blob) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        const url = URL.createObjectURL(blob);

        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);

            canvas.toBlob((pngBlob) => {
                URL.revokeObjectURL(url);
                if (pngBlob) resolve(pngBlob);
                else reject(new Error('Canvas to Blob conversion failed'));
            }, 'image/png');
        };

        img.onerror = () => {
            URL.revokeObjectURL(url);
            reject(new Error('Failed to load image for conversion'));
        };

        img.src = url;
    });
}

function createObjectURLWithAutoRevoke(blob, revokeTime=60000) {
    const url = window.URL.createObjectURL(blob);
    setTimeout(() => {
        window.URL.revokeObjectURL(url);
    }, revokeTime);
    return url;
}

function downloadFileByUrl(url) {
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function querySelectorVisible(root, selector) {
    const elements = root.querySelectorAll(selector);
    for (const element of elements) {
        if (uiElementIsVisible(element)) {
            return element;
        }
    }
    return null;
}

function querySelectorVisibleAll(root, selector) {
    const elements = root.querySelectorAll(selector);
    const visibleElements = [];
    for (const element of elements) {
        if (uiElementIsVisible(element)) {
            visibleElements.push(element);
        }
    }
    return visibleElements;
}

function clickVisibleButtons(selector) {
    const buttons = querySelectorVisibleAll(document, selector);
    for (const button of buttons) {
        button.click();
    }
}
