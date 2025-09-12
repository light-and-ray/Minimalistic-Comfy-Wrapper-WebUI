
window.addEventListener('beforeunload', (event) => {
    event.preventDefault();
    event.returnValue = "Are you sure";
});

[...document.getElementsByClassName('cm-content')].forEach(elem => elem.setAttribute('spellcheck', 'true'));
