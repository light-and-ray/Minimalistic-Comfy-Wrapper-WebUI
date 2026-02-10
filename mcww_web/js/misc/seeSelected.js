
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

onUiUpdate((updatedElements, removedElements) => {
    const addedTargetElements = updatedElements.querySelectorAll('.scroll-to-selected');
    addedTargetElements.forEach((el) => {
        if (!observedElements.has(el)) {
            observedElements.add(el);
            scrollSelectedIntoView(el);
        }
    });
    const removedTargetElements = removedElements.querySelectorAll('.scroll-to-selected');
    removedTargetElements.forEach((el) => {
        observedElements.delete(el);
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

