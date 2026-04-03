
function scrollSelectedIntoView(element) {
    const selected = element.querySelector('.selected');
    if (selected) {
        function getScrollParent(node) {
            if (!node || node === document.body || node === document.documentElement) {
                return document.documentElement;
            }
            const style = window.getComputedStyle(node);
            const overflowRegex = /(auto|scroll)/;
            if (overflowRegex.test(style.overflow + style.overflowY + style.overflowX)) {
                return node;
            }
            return getScrollParent(node.parentNode);
        }

        requestAnimationFrame(() => {
            const scrollContainer = getScrollParent(selected);
            const containerRect = scrollContainer.getBoundingClientRect();
            const selectedRect = selected.getBoundingClientRect();
            const relativeTop = selectedRect.top - containerRect.top;
            const relativeLeft = selectedRect.left - containerRect.left;
            const targetScrollTop = relativeTop - (containerRect.height / 2) + (selectedRect.height / 2);
            const targetScrollLeft = relativeLeft - (containerRect.width / 2) + (selectedRect.width / 2);
            scrollContainer.scrollTop += targetScrollTop;
            scrollContainer.scrollLeft += targetScrollLeft;
        });
    }
}


const observedElements = new WeakSet();

function scrollSelectedOnPageChanged() {
    const elements = document.querySelectorAll('.scroll-to-selected');
    elements.forEach((element) => {
        scrollSelectedIntoView(element);
    });
}

onPageSelected(scrollSelectedOnPageChanged);


function scrollSelectedOnQueuePrioritySelected() {
    waitForElement(document, ".mcww-queue-radio:has(.selected:not(.mcww-hidden))", (radio) => {
        scrollSelectedIntoView(radio);
    }, 1000);
}


function scrollSelectedOnChange() {
    const selectedElements = document.querySelectorAll('.scroll-to-selected .selected');
    selectedElements.forEach((selected) => {
        if (!uiElementIsVisible(selected)) return;
        if (selected.querySelector("input")?.value === "-1") return;
        selected.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
        });
    });
}


onUiUpdate((updatedElements) => {
    updatedElements.querySelectorAll('.scroll-to-selected.on-render').forEach((element) => scrollSelectedIntoView(element));
});
