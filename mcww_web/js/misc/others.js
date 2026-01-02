
onUiUpdate(() => {
    const tabButtons = document.querySelectorAll('.project-media-prompt-tabs .tab-container button[role="tab"]');
    const tabPanels = document.querySelectorAll('.project-media-prompt-tabs div[role="tabpanel"]');
    tabPanels.forEach((panel, index) => {
        const hasMedia = panel.querySelector('img, video') !== null;
        if (tabButtons[index]) {
            if (hasMedia) {
                tabButtons[index].classList.add('has-media');
            } else {
                tabButtons[index].classList.remove('has-media');
            }
        }
    });
});

onUiUpdate(() => {
    document.querySelectorAll(".cm-content").forEach(elem => elem.setAttribute('spellcheck', 'true'));
});


function onRunButtonCopyClick() {
    document.querySelector('.mcww-run-button')?.click();
}


onUiLoaded(() => {
    if (!OPTIONS.preventPullToRefreshGesture) return;
    let startY = 0;
    let isPullingDown = false;

    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
            isPullingDown = true;
        }
    }, { passive: false });

    document.addEventListener('touchmove', function(e) {
        if (!isPullingDown || window.scrollY !== 0) return;
        const currentY = e.touches[0].clientY;
        const diff = currentY - startY;
        // Only trigger if pulling down (diff > 0)
        if (diff > 0) {
            e.preventDefault();
        }
    }, { passive: false });

    document.addEventListener('touchend', function() {
        if (isPullingDown) {
            document.body.style.overflowY = '';
            isPullingDown = false;
        }
    }, { passive: false });
});
