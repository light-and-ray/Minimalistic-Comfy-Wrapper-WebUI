
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

function getContentWidth(element) {
    let widthWithPaddings = element.clientWidth;
    const elementComputedStyle = window.getComputedStyle(element, null);
    return (
        widthWithPaddings - parseFloat(elementComputedStyle.paddingLeft) - parseFloat(elementComputedStyle.paddingRight)
    );
}


function uiElementIsVisible(element) {
    if (!element) {
        return false;
    }
    if (element === document) {
        return true;
    }

    if (element.nodeType !== Node.ELEMENT_NODE) {
        return uiElementIsVisible(element.parentNode);
    }

    const computedStyle = getComputedStyle(element);

    const isVisible = (
        computedStyle.display !== 'none' &&
        computedStyle.visibility !== 'hidden' &&
        parseFloat(computedStyle.opacity) > 0
    );

    if (!isVisible) return false;

    return uiElementIsVisible(element.parentNode);
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


function isTabsOverflowMenuOpen() {
    const overflowMenus = document.querySelectorAll('.overflow-dropdown');
    return Array.from(overflowMenus).some(menu => uiElementIsVisible(menu));
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
