
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

function attachFullscreenHandlers(element, container) {
    element.addEventListener('click', () => {
        const fullscreenButton = container.querySelector('button[title="Fullscreen"]');
        if (fullscreenButton) {
            fullscreenButton.click();
        }
    });
    element.addEventListener('dblclick', () => {
        const fullscreenButton = container.querySelector('button[title="Exit fullscreen mode"]');
        if (fullscreenButton) {
            fullscreenButton.click();
        }
    });
}

function attachFullscreenClick() {
    const galleryContainers = document.querySelectorAll('.gallery-container');

    galleryContainers.forEach(container => {
        const previewButton = container.querySelector('button.preview');
        const thumbnailItems = container.querySelectorAll('button.thumbnail-small');

        if (previewButton && thumbnailItems.length === 1) {
            const mediaButton = container.querySelector('button.media-button');

            if (mediaButton) {
                if (!mediaButton.dataset.fullscreenClickAttached) {
                    thumbnailItems[0].parentElement.style.display = "none";
                    mediaButton.classList.add("mcww-full-screen-media-button");
                    attachFullscreenHandlers(mediaButton, container);
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
                attachFullscreenHandlers(image, container);
                image.dataset.fullscreenClickAttached = 'true';
            }
        }
    });

}

onUiUpdate(attachFullscreenClick);
