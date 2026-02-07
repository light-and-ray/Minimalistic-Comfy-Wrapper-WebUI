
// fix galleries ugly previews

function fixGalleries() {
    const galleryContainers = document.querySelectorAll('.gallery-container');
    galleryContainers.forEach(container => {
        if (container.closest('div.upload-gallery')) {
            return;
        }
        const previewButton = container.querySelector('button.preview');
        if (!previewButton) {
            const thumbnailButton = container.querySelector('button.thumbnail-item');
            if (thumbnailButton) {
                thumbnailButton.click();
            }
        }
        const videoItems = container.querySelectorAll('video');
        videoItems.forEach((videoItem) => {
            videoItem.loop = true;
            videoItem.volume = OPTIONS.defaultVideosVolume;
        })
    });
}

onUiUpdate(fixGalleries);


// handle fullscreen


function globalExitFullscreenIfExists() {
    const exitFullscreenButton = document.querySelector('button[title="Exit fullscreen mode"]');
    if (exitFullscreenButton) {
        exitFullscreenButton.click();
    }
}

function attachFullscreenButtonFix(container) {
    const fullscreenButton = container.querySelector('button[title="Fullscreen"]');
    if (fullscreenButton && !fullscreenButton.dataset.fixAttached) {
        fullscreenButton.addEventListener('click', () => {
            container.style.position = "initial";
            fullscreenButton.dataset.fixAttached = "false";
            const currentUrl = window.location.href;
            pushState({triggered: "openedFullscreen"}, currentUrl);
        });
        fullscreenButton.dataset.fixAttached = "true";
    }
    const exitFullscreenButton = container.querySelector('button[title="Exit fullscreen mode"]');
    if (exitFullscreenButton && !exitFullscreenButton.dataset.fixAttached) {
        exitFullscreenButton.addEventListener('click', () => {
            container.style.position = "relative";
            exitFullscreenButton.dataset.fixAttached = "false";
            if (history.state && history.state.triggered === "openedFullscreen") {
                goBack();
            }
        });
        exitFullscreenButton.dataset.fixAttached = "true";
    }
}

onPopState(globalExitFullscreenIfExists);


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

        if (!container.querySelector('video')) {
            // Clean up if there are more than 1 thumbnail items
            if (thumbnailItems.length > 1 && mediaButton && mediaButton.dataset.fullscreenClickAttached) {
                detachFullscreenHandlers(mediaButton);
                delete mediaButton.dataset.fullscreenClickAttached;
            }
            // Attach if there's exactly 1 thumbnail item
            else if (previewButton && thumbnailItems.length === 1 && mediaButton) {
                if (!mediaButton.dataset.fullscreenClickAttached) {
                    attachFullscreenHandlers(mediaButton, container);
                    mediaButton.dataset.fullscreenClickAttached = 'true';
                }
            }
        }

        if (thumbnailItems.length > 1) {
            thumbnailItems[0].parentElement.style.display = "";
            if (mediaButton) {
                mediaButton.classList.remove("mcww-full-height-media-button");
            }
        } else if (thumbnailItems.length === 1) {
            thumbnailItems[0].parentElement.style.display = "none";
            if (mediaButton) {
                mediaButton.classList.add("mcww-full-height-media-button");
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
