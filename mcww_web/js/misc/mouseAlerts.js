
function mouseAlert(message, duration = 350) {
    const alertElement = document.createElement('div');
    alertElement.className = 'mouse-alert';
    alertElement.textContent = message;

    const progressBar = document.createElement('div');
    progressBar.className = 'mouse-alert-progress';
    alertElement.appendChild(progressBar);

    const positionAtCursor = (e) => {
        const viewport = window.visualViewport || {
            scale: 1,
            offsetLeft: 0,
            offsetTop: 0,
            width: window.innerWidth,
            height: window.innerHeight
        };
        let scale = 1 / viewport.scale;

        let { width: elementWidth, height: elementHeight } = getFullElementSize(alertElement);
        elementWidth *= scale;
        elementHeight *= scale;
        const offsetY = 7 * scale;
        const maxX = viewport.offsetLeft + viewport.width - elementWidth;
        const maxY = viewport.offsetTop + viewport.height - elementHeight;
        const minX = viewport.offsetLeft;
        const minY = viewport.offsetTop;

        const x = clamp(e.clientX - elementWidth / 2, minX, maxX);
        const y = clamp(e.clientY + elementHeight / 2 + offsetY, minY, maxY);

        alertElement.style.left = `${x}px`;
        alertElement.style.top = `${y}px`;
        alertElement.style.transform = `scale(${scale})`;
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



