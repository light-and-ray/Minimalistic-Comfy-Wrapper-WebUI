
function isPreferredThemeDark() {
    if (OPTIONS.preferredThemeDarkLight === "System") {
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    } else {
        return (OPTIONS.preferredThemeDarkLight === "Dark");
    }
}


onUiLoaded(() => {
    function updateUrlParameter(key, value) {
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

    function syncArgAndClass() {
        if (isPreferredThemeDark()) {
            if (!document.body.classList.contains('dark')) {
                updateUrlParameter('__theme', 'light');
            } else {
                deleteUrlParameter('__theme');
            }
        } else {
            if (document.body.classList.contains('dark')) {
                updateUrlParameter('__theme', 'dark');
            } else {
                deleteUrlParameter('__theme');
            }
        }
    }

    function toggleDarkMode() {
        document.body.classList.toggle('dark');
        syncArgAndClass();
    }

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
    syncArgAndClass();
});
