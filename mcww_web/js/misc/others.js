

onUiUpdate(() => {
    document.querySelectorAll(".cm-content").forEach(elem => elem.setAttribute('spellcheck', 'true'));
});


function applyPreventPullToRefresh() {
    if (!OPTIONS.preventPullToRefreshGesture) return;
    let startY = 0;
    let isPullingDown = false;

    document.addEventListener('touchstart', function(e) {
        if (window.scrollY !== 0) return;
        const touch = e.touches[0];
        const element = document.elementFromPoint(touch.clientX, touch.clientY);
        if (isScrollableTop(element)) {
            isPullingDown = false;
            return;
        }
        startY = touch.clientY;
        isPullingDown = true;
    }, { passive: false });

    document.addEventListener('touchmove', function(e) {
        if (!isPullingDown || window.scrollY !== 0 || e.touches.length > 1) return;
        const currentY = e.touches[0].clientY;
        const diff = currentY - startY;
        if (diff > 0) {
            e.preventDefault();
        }
    }, { passive: false });

    document.addEventListener('touchend', function() {
        if (isPullingDown) {
            isPullingDown = false;
        }
    }, { passive: false });
}

onUiLoaded(applyPreventPullToRefresh);

