
function isPreferredThemeDark() {
    if (OPTIONS.preferredThemeDarkLight === "System") {
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    } else {
        return (OPTIONS.preferredThemeDarkLight === "Dark");
    }
}


function _syncThemeArgAndClass() {
    if (isPreferredThemeDark()) {
        if (!document.body.classList.contains('dark')) {
            setUrlParameter('__theme', 'light');
        } else {
            deleteUrlParameter('__theme');
        }
    } else {
        if (document.body.classList.contains('dark')) {
            setUrlParameter('__theme', 'dark');
        } else {
            deleteUrlParameter('__theme');
        }
    }
}


function toggleDarkMode() {
    document.body.classList.toggle('dark');
    _syncThemeArgAndClass();
}


onUiLoaded(() => {
    function onToggleDarkLightClick(event) {
        const elementsAtPoint = document.elementsFromPoint(event.clientX, event.clientY);
        for (const elementAtPoint of elementsAtPoint) {
            if (!elementAtPoint.classList.contains("toggle-dark-mode") && elementAtPoint.tagName === "BUTTON") {
                setTimeout(() => {elementAtPoint.click();}, 10);
                return;
            }
        }
        toggleDarkMode();
    }
    const button = document.createElement('button');
    button.textContent = '☀️/🌙';
    button.classList.add('toggle-dark-mode');
    if (!OPTIONS.showToggleDarkLightButton) {
        button.classList.add('mcww-zero-opacity');
    }
    button.onclick = onToggleDarkLightClick;

    document.body.appendChild(button);

    if (!getUrlParameter("__theme")) {
        if (isPreferredThemeDark() !== document.body.classList.contains('dark')) {
            toggleDarkMode();
        }
    }
    _syncThemeArgAndClass();
});
