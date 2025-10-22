
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


function attachFullscreenButtonFix(container) {
    const fullscreenButton = container.querySelector('button[title="Fullscreen"]');
    if (fullscreenButton && !fullscreenButton.dataset.fixAttached) {
        fullscreenButton.addEventListener('click', () => {
            container.style.position = "initial";
            fullscreenButton.dataset.fixAttached = "false";
        });
        fullscreenButton.dataset.fixAttached = "true";
    }
    const exitFullscreenButton = container.querySelector('button[title="Exit fullscreen mode"]');
    if (exitFullscreenButton && !exitFullscreenButton.dataset.fixAttached) {
        exitFullscreenButton.addEventListener('click', () => {
            container.style.position = "relative";
            exitFullscreenButton.dataset.fixAttached = "false";
        });
        exitFullscreenButton.dataset.fixAttached = "true";
    }
}


function attachFullscreenHandlers(element, container) {
    const clickHandler = () => {
        const fullscreenButton = container.querySelector('button[title="Fullscreen"]');
        if (fullscreenButton) {
            fullscreenButton.click();
        }
    };

    const dblClickHandler = () => {
        const fullscreenButton = container.querySelector('button[title="Exit fullscreen mode"]');
        if (fullscreenButton) {
            fullscreenButton.click();
        }
    };

    element.addEventListener('click', clickHandler);
    element.addEventListener('dblclick', dblClickHandler);
    element._fullscreenHandlers = { clickHandler, dblClickHandler };
}


function detachFullscreenHandlers(element) {
    if (element._fullscreenHandlers) {
        element.removeEventListener('click', element._fullscreenHandlers.clickHandler);
        element.removeEventListener('dblclick', element._fullscreenHandlers.dblClickHandler);
        delete element._fullscreenHandlers;
    }
}

function attachFullscreenClick() {
    const galleryContainers = document.querySelectorAll('.gallery-container');
    galleryContainers.forEach(container => {
        attachFullscreenButtonFix(container);
        const previewButton = container.querySelector('button.preview');
        const thumbnailItems = container.querySelectorAll('button.thumbnail-small');
        const mediaButton = container.querySelector('button.media-button');

        // Clean up if there are more than 1 thumbnail items
        if (thumbnailItems.length > 1 && mediaButton && mediaButton.dataset.fullscreenClickAttached) {
            detachFullscreenHandlers(mediaButton);
            mediaButton.classList.remove("mcww-full-screen-media-button");
            thumbnailItems[0].parentElement.style.display = "";
            delete mediaButton.dataset.fullscreenClickAttached;
        }
        // Attach if there's exactly 1 thumbnail item
        else if (previewButton && thumbnailItems.length === 1 && mediaButton) {
            if (!mediaButton.dataset.fullscreenClickAttached) {
                thumbnailItems[0].parentElement.style.display = "none";
                mediaButton.classList.add("mcww-full-screen-media-button");
                attachFullscreenHandlers(mediaButton, container);
                mediaButton.dataset.fullscreenClickAttached = 'true';
            }
        }
    });

    const imageContainers = document.querySelectorAll('.image-container');
    imageContainers.forEach(container => {
        attachFullscreenButtonFix(container);
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
