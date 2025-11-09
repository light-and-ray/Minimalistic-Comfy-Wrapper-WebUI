
onUiLoaded(() => {
    function updateUrlParameter(key, value) {
        var url = new URL(window.location.href);
        url.searchParams.set(key, value);
        history.replaceState(null, '', url.href);
    }

    function deleteUrlParameter(key) {
        var url = new URL(window.location.href);
        url.searchParams.delete(key);
        history.replaceState(null, '', url.href);
    }

    function syncArgAndClass() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
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

    function onClick(event) {
        const elementsAtPoint = document.elementsFromPoint(event.clientX, event.clientY);
        for (const elementAtPoint of elementsAtPoint) {
            if (!elementAtPoint.classList.contains("toggle-dark-mode") && elementAtPoint.tagName === "BUTTON") {
                setTimeout(() => {elementAtPoint.click();}, 100);
                return;
            }
        }
        toggleDarkMode();
    }

    const button = document.createElement('button');
    button.textContent = '☀️/🌙';
    button.className = 'toggle-dark-mode';
    button.onclick = onClick;

    document.body.appendChild(button);

});
