
function fixGalleries() {
    const galleryContainers = document.querySelectorAll('.gallery-container');
    galleryContainers.forEach(container => {
        const previewButton = container.querySelector('button.preview');
        if (!previewButton) {
            const thumbnailButton = container.querySelector('button.thumbnail-item');
            if (thumbnailButton) {
                thumbnailButton.click();
            }
        }
    });
}

onUiUpdate(fixGalleries);


function attachFullscreenClick() {
    const galleryContainers = document.querySelectorAll('.gallery-container');

    galleryContainers.forEach(container => {
        const previewButton = container.querySelector('button.preview');
        const thumbnailItems = container.querySelectorAll('button.thumbnail-small');

        // Check if there is a preview button and exactly one thumbnail item
        if (previewButton && thumbnailItems.length === 1) {
            const mediaButton = container.querySelector('button.media-button');

            if (mediaButton) {
                if (!mediaButton.dataset.fullscreenClickAttached) {
                    thumbnailItems[0].parentElement.style.display = "none";
                    mediaButton.classList.add("mcww-full-screen-media-button");

                    mediaButton.addEventListener('click', () => {
                        const fullscreenButton = container.querySelector(
                                'button[title="Fullscreen"], button[title="Exit fullscreen mode"]');
                        if (fullscreenButton) {
                            fullscreenButton.click();
                        }
                    });
                    // Mark the event as attached
                    mediaButton.dataset.fullscreenClickAttached = 'true';
                }
            }
        }
    });
    const imageContainers = document.querySelectorAll('.image-container');
    imageContainers.forEach(container => {
        const images = container.querySelectorAll('img');
        if (images.length === 1) {
            const image = images[0];
            if (!image.dataset.fullscreenClickAttached) {
                image.addEventListener('click', () => {
                    const fullscreenButton = container.querySelector(
                            'button[title="Fullscreen"], button[title="Exit fullscreen mode"]');
                    if (fullscreenButton) {
                        fullscreenButton.click();
                    }
                });
                image.dataset.fullscreenClickAttached = 'true';
            }
        }
    });

}

onUiUpdate(attachFullscreenClick);
