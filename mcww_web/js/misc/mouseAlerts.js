
function mouseAlert(message, duration = 350) {
    const alertElement = document.createElement('div');
    alertElement.className = 'mouse-alert';
    alertElement.textContent = message;

    const progressBar = document.createElement('div');
    progressBar.className = 'mouse-alert-progress';
    alertElement.appendChild(progressBar);

    const positionAtCursor = (e) => {
        const elementWidth = alertElement.clientWidth;
        const elementHeight = alertElement.clientHeight;
        const offsetY = 7;
        const minYGap = 12;

        const maxX = window.innerWidth - elementWidth / 2;
        const maxY = window.innerHeight - elementHeight / 2 - offsetY;
        const minX = 0 + elementWidth / 2;
        const minY = 0 + elementHeight / 2 + offsetY + minYGap;

        const x = Math.min(Math.max(e.clientX, minX), maxX);
        const y = Math.min(Math.max(e.clientY - offsetY, minY), maxY);

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

    positionAtCursor(getLastMouseEvent());
}



