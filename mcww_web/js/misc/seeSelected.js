
function scrollSelectedIntoView(element) {
    const selected = element.querySelector('.selected');
    if (selected) {
        requestAnimationFrame(() => {
            selected.scrollIntoView({
                behavior: 'instant',
                block: 'center',
                inline: 'center',
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

function scrollSelectedOnQueuePrioritySelected() {
    waitForElement(".mcww-queue-radio:has(.selected:not(.mcww-hidden))", (radio) => {
        scrollSelectedIntoView(radio);
    }, 1000);
}

onPageSelected(scrollSelectedOnPageChanged);


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

