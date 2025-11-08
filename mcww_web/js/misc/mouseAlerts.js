
function mouseAlert(message, duration = 350) {
    const alertElement = document.createElement('div');
    alertElement.className = 'mouse-alert';
    alertElement.textContent = message;

    const progressBar = document.createElement('div');
    progressBar.className = 'mouse-alert-progress';
    alertElement.appendChild(progressBar);

    const positionAtCursor = (e) => {
        const x = e ? e.clientX : window.innerWidth / 2;
        const y = e ? e.clientY + 57 : window.innerHeight / 2;
        alertElement.style.left = `${x}px`;
        alertElement.style.top = `${y}px`;
    };

    document.body.appendChild(alertElement);

    // Animate progress bar
    progressBar.style.transitionDuration = `${duration}ms`;
    setTimeout(() => {
        progressBar.style.transform = 'scaleX(0)';
    }, 10);

    setTimeout(() => {
        alertElement.remove();
    }, duration);

    const lastMouseEvent = window.lastMouseEvent || { clientX: window.innerWidth / 2, clientY: window.innerHeight / 2 };
    positionAtCursor(lastMouseEvent);
}

document.addEventListener('mousemove', (e) => {
    window.lastMouseEvent = e;
});

