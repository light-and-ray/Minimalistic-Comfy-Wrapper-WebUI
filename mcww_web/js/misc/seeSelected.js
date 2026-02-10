
function scrollSelectedIntoView(element) {
    const selected = element.querySelector('.selected');
    if (selected) {
        requestAnimationFrame(() => {
            selected.scrollIntoView({
                behavior: 'instant',
                block: 'center',
            });
        });
    }

}


const observedElements = new WeakSet();

onUiUpdate((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                const newElements = node.querySelectorAll('.scroll-to-selected');
                newElements.forEach((el) => {
                    if (!observedElements.has(el)) {
                        observedElements.add(el);
                        scrollSelectedIntoView(el);
                    }
                });
            }
        });
        mutation.removedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                const removedElements = node.querySelectorAll('.scroll-to-selected');
                removedElements.forEach((el) => {
                    observedElements.delete(el);
                });
            }
        });
    });
});


function scrollSelectedOnChange() {
    const selectedElements = document.querySelectorAll('.scroll-to-selected .selected');
    selectedElements.forEach((selected) => {
        selected.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
        });
    });
}

