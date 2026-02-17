
// fix galleries ugly previews and set video settings

onUiLoaded(() => {
    if (getSessionStorageVariable("volumeForNewVideos") === null) {
        setSessionStorageVariable("volumeForNewVideos", OPTIONS.defaultVideosVolume);
    }
});

function fixGalleries(updatedElements) {
    const galleryContainers = updatedElements.querySelectorAll('.gallery-container');
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
            videoItem.volume = getSessionStorageVariable("volumeForNewVideos", 1);
            addEventListenerWithCleanup(videoItem, "volumechange", (event) => {
                setSessionStorageVariable("volumeForNewVideos", videoItem.volume);
            });
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
        addEventListenerWithCleanup(fullscreenButton, 'click', () => {
            container.style.position = "initial";
            fullscreenButton.dataset.fixAttached = "false";
            const currentUrl = window.location.href;
            pushState({triggered: "openedFullscreen"}, currentUrl);
        });
        fullscreenButton.dataset.fixAttached = "true";
    }
    const exitFullscreenButton = container.querySelector('button[title="Exit fullscreen mode"]');
    if (exitFullscreenButton && !exitFullscreenButton.dataset.fixAttached) {
        addEventListenerWithCleanup(exitFullscreenButton, 'click', () => {
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

    addEventListenerWithCleanup(element, 'click', clickHandler);
    addEventListenerWithCleanup(element, 'dblclick', dblClickHandler);
    element._fullscreenHandlers = { clickHandler, dblClickHandler };
}


function detachFullscreenHandlers(element) {
    if (element._fullscreenHandlers) {
        element.removeEventListener('click', element._fullscreenHandlers.clickHandler);
        element.removeEventListener('dblclick', element._fullscreenHandlers.dblClickHandler);
        delete element._fullscreenHandlers;
    }
}

function attachFullscreenClick(updatedElements) {
    const galleryContainers = updatedElements.querySelectorAll('.gallery-container');
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

    const imageContainers = updatedElements.querySelectorAll('.image-container');
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


function updatePseudoGallerySelectedStyles() {
    const pseudoGalleries = document.querySelectorAll(".mcww-pseudo-gallery");
    pseudoGalleries.forEach((pseudoGallery) => {
        const indexElement = pseudoGallery.querySelector(".selected-index textarea");
        let selectedIndex = parseInt(indexElement.value) || 0;
        const items = pseudoGallery.querySelectorAll("button.gallery-item");
        if (items.length === 0) {
            return;
        }
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add("selected");
            } else {
                item.classList.remove("selected");
            }
        });
    });
}

function selectProperElementInPseudoGalleries() {
    const pseudoGalleries = document.querySelectorAll(".mcww-pseudo-gallery");
    pseudoGalleries.forEach((pseudoGallery) => {
        const indexElement = pseudoGallery.querySelector(".selected-index textarea");
        let selectedIndex = parseInt(indexElement.value) || 0;
        const items = pseudoGallery.querySelectorAll("button.gallery-item");
        if (items.length === 0) {
            return;
        }
        if (selectedIndex >= items.length) {
            selectedIndex = items.length - 1;
        }
        items[selectedIndex].click();
    });
}
onWorkflowRendered(selectProperElementInPseudoGalleries);


function applyCloseOnDragOver(updatedElements) {
    const elements = updatedElements.querySelectorAll(".mcww-other-gallery:not(.drag-over-patched)");
    if (elements.length > 0) {
        elements.forEach((element) => {
            element.classList.add("drag-over-patched");
            addEventListenerWithCleanup(element, "dragover", (e) => {
                const hasFiles = e.dataTransfer && Array.from(e.dataTransfer.types).includes('Files');
                if (!hasFiles) {
                    return;
                }
                e.preventDefault();
                const clearButton = element.querySelector("button[title='Clear']");
                if (clearButton) {
                    clearButton.click();
                }
            });
        });
    }
}

onUiUpdate(applyCloseOnDragOver);
