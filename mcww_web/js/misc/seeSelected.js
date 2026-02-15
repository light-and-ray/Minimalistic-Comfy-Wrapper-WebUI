
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

function scrollSelectedOnPageChanged() {
    const elements = document.querySelectorAll('.scroll-to-selected');
    elements.forEach((element) => {
        scrollSelectedIntoView(element);
    });
}

onPageSelected(scrollSelectedOnPageChanged);


function scrollSelectedOnChange() {
    const selectedElements = document.querySelectorAll('.scroll-to-selected .selected');
    selectedElements.forEach((selected) => {
        selected.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
        });
    });
}

