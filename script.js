
window.addEventListener('beforeunload', (event) => {
    // event.preventDefault();
    event.returnValue = "";
});

[...document.getElementsByClassName('cm-content')].forEach(elem => elem.setAttribute('spellcheck', 'true'));
