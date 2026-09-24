

function trySelectTab(tabNumber) {
    const tabsContainers = document.querySelectorAll('.mcww-page-tabs');
    tabsContainers.forEach((tabsContainer) => {
        if (!uiElementIsVisible(tabsContainer)) {
            return;
        }
        const tabs = tabsContainer.querySelectorAll('button[role="tab"], .overflow-dropdown button');
        if (tabNumber >= 1 && tabNumber <= tabs.length) {
            tabs[tabNumber - 1].click();
        }
    });
}


function activeElementEditable() {
    return document.activeElement.matches('textarea, input[type="text"], input[type="number"], ' +
                                                'input:not([type]), div.cm-content')
}


function dispatchSyntheticKey(originalEvent, code, key) {
    const syntheticEvent = new KeyboardEvent(originalEvent.type, {
        code: code,
        key: key,
        bubbles: originalEvent.bubbles,
        cancelable: originalEvent.cancelable,
        composed: originalEvent.composed,
        ctrlKey: originalEvent.ctrlKey,
        altKey: originalEvent.altKey,
        shiftKey: originalEvent.shiftKey,
        metaKey: originalEvent.metaKey,
        repeat: originalEvent.repeat
    });

    const target = originalEvent.target || document;
    target.dispatchEvent(syntheticEvent);
}


function tryModifySlider(difference, selector) {
    const sliders = document.querySelectorAll(selector);
    sliders.forEach((slider) => {
        if (!uiElementIsVisible(slider)) return;
        const currentValue = parseFloat(slider.value);
        const minValue = parseFloat(slider.min);
        const maxValue = parseFloat(slider.max);
        let newValue = currentValue + difference;
        if (newValue < minValue) newValue = minValue;
        if (newValue > maxValue) newValue = maxValue;
        slider.value = newValue;
        const event = new Event('input', {
            bubbles: true,
            cancelable: true,
        });
        slider.dispatchEvent(event);
    });
}


document.addEventListener('keydown', (event) => {
    const isCtrl = event.ctrlKey || event.metaKey;
    const lastMouseEvent = getLastMouseEvent();
    const inGalleryFullscreen = document.querySelector(".block.fullscreen");
    const galleryContainer = getGalleryContainerUnderCursor();
    const galleryVideo = galleryContainer?.querySelector('.media-button>video, .mirror-wrap>video');
    let needVolumeHotkeys = galleryVideo && !galleryVideo.muted && videoHasAudio(galleryVideo);
    if (getSelectedMainUIPage() === "queue" && !inGalleryFullscreen) {
        needVolumeHotkeys = false;
    }

    if (event.altKey && event.code === "KeyV") {
        new McwwClipboardHistoryMenu(lastMouseEvent);
        event.preventDefault();
    }
    if (event.code === "Escape") {
        event.stopPropagation(); // block gradio's behavior when it selects the first element in gallery on escape
        if (querySelectorVisible(document, ".mcww-menu")) {
            return;
        }
    }

    if (isCtrl && event.code === "KeyL") {
        const focusElements = document.querySelectorAll(".mcww-loras-filter textarea, .presets-filter textarea");
        for (const focusElement of focusElements) {
            if (!uiElementIsVisible(focusElement)) continue;
            event.preventDefault();
            focusElement.focus();
            focusElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            focusElement.select();
            break;
        }
    }

    if (isCtrl && !event.shiftKey && event.code === "KeyS") {
        event.preventDefault();
        clickVisibleButtons(document, ".mcww-save-button");
    }
    if (isCtrl && event.shiftKey && event.code === "KeyS") {
        event.preventDefault();
        clickVisibleButtons(document, ".mcww-shift-save-button");
    }

    if (event.code == "F5" || event.code == "KeyR" && isCtrl) {
        const reloadButton = document.querySelector(".mcww-reload-ui-button");
        if (reloadButton) {
            event.preventDefault();
            reloadButton.click();
        }
        g_waitingForReload = true;
    }

    if (isCtrl && event.code === "Enter") {
        clickVisibleButtons(document, '.mcww-run-button');
        event.preventDefault();
    }


    if (activeElementEditable()) {
        if (event.code === "Escape") {
            document.activeElement.blur();
        }
        return;
    }


    if (document.fullscreenElement?.matches("video") && (event.code === "Escape" || event.code === "KeyF")) {
        document.exitFullscreen();
        return;
    } else if (!OPTIONS.holdEscapeToExitUIFullscreen && isUIInFullscreen() && event.code === "Escape") {
        toggleUIFullScreen();
    } else if (event.code == "F11" || event.code === "KeyF" && (event.shiftKey || event.altKey)) {
        event.preventDefault();
        toggleUIFullScreen();
    }

    const opacityDiff = 0.03;
    if (event.code === "Equal" || event.code == "NumpadAdd") {
        tryModifySlider(+opacityDiff, '.opacity-slider input[type="range"]');
    }
    if (event.code === "Minus" || event.code == "NumpadSubtract") {
        tryModifySlider(-opacityDiff, '.opacity-slider input[type="range"]');
    }
    if (event.code === "KeyS" && !event.shiftKey && !isCtrl) {
        clickVisibleButtons(document, 'button.mcww-swap, .mcww-swap input');
    }
    if (event.code === "KeyT") {
        document.querySelector("button.toggle-dark-mode")?.click();
    }

    if (!inGalleryFullscreen) {
        if (event.code === "Escape") {
            closeSidebarOnMobile();
            clickVisibleButtons(document, ".click-on-escape, button.toast-close, div.api-docs>div.backdrop");
            removeTrailingQuestionMarkInUrl();
        }
        if (event.code === "KeyR" && !isCtrl) {
            clickVisibleButtons(document, ".mcww-refresh");
        }
        if (event.code === "KeyA") {
            clickVisibleButtons(document, '.mcww-auto-refresh-checkbox input');
        }
        if (event.code === "KeyQ") {
            openPageOrGoBack("queue");
        }
        if (event.code === "KeyP") {
            ensureProjectIsSelected();
        }
        if (event.code === "KeyH") {
            openPageOrGoBack("helpers");
        }
        if (event.code === "KeyO") {
            openPageOrGoBack("options");
        }
        if (!needVolumeHotkeys) {
            if (event.altKey || isCtrl) {
                if (event.code === "ArrowUp") {
                    clickVisibleButtons(document, ".mcww-queue-move-up");
                }
                if (event.code === "ArrowDown") {
                    clickVisibleButtons(document, ".mcww-queue-move-down");
                }
            } else {
                if (event.code === "ArrowUp") {
                    trySelectPreviousQueueEntry();
                }
                if (event.code === "ArrowDown") {
                    trySelectNextQueueEntry();
                }
            }
        }
        if (
            (event.code >= "Digit1" && event.code <= "Digit9") ||
            (event.code >= "Numpad1" && event.code <= "Numpad9")
        ) {
            const enteredNumber = parseInt(event.code.replace(/Digit|Numpad/g, ""));
            trySelectTab(enteredNumber);
            trySelectTool(enteredNumber);
            trySelectQueuePriority(enteredNumber);
        }
        const brushSizeDiff = 0.5;
        if (event.code === "BracketRight" || event.code == "NumpadAdd") {
            tryModifySlider(+brushSizeDiff, '#brushSizeInput input[type="range"]');
        }
        if (event.code === "BracketLeft") {
            tryModifySlider(-brushSizeDiff, '#brushSizeInput input[type="range"]');
        }
        if (event.code === "KeyZ" && isCtrl) {
            if (event.shiftKey) {
                clickVisibleButtons(document, "button.mcww-redo");
            } else {
                clickVisibleButtons(document, "button.mcww-undo");
            }
        }
        if (event.code === "KeyY" && isCtrl) {
            clickVisibleButtons(document, "button.mcww-redo");
        }
        if (event.code === "KeyC") {
            clickVisibleButtons(document, "#colorPicker");
            if (getSelectedMainUIPage() === "compare") {
                goBack();
            }
        }
        if (event.code === "Backquote") {
            document.querySelector('.sidebar .toggle-button')?.click();
        }
    }
    else { // inGalleryFullscreen
        if (event.code === "KeyQ") {
            globalExitFullscreenIfExists();
        }
        if (event.code === "Escape") {
            globalExitFullscreenIfExists();
        }
    }

    if (event.code === "KeyW" && isCtrl && event.shiftKey && event.altKey && isInsidePWA()) {
        openPageOrGoBack("wolf3d"); // in not PWA user can change page directly in address bar
    }

    if (event.code === "Space") {
        event.preventDefault();
    }

    if (galleryContainer) {
        if (event.code === "KeyS") {
            clickVisibleButtons(galleryContainer, 'button[title="Download"], .download-text, .swap-resolution');
        }

        if (event.code === "KeyF") {
            let clickEnterFullscreen = true;
            let clickExitFullscreen = true;
            if (event.shiftKey || event.altKey) {
                if (isUIInFullscreen()) {
                    // Don't enter gallery fullscreen when user's intention is to exit ui fullscreen
                    clickEnterFullscreen = false;
                } else {
                    // Don't exit gallery fullscreen when user's intention is to enter ui fullscreen
                    clickExitFullscreen = false;
                }
            }
            if (clickEnterFullscreen) {
                clickVisibleButtons(galleryContainer, 'button[title="Fullscreen"]');
            }
            if (clickExitFullscreen) {
                clickVisibleButtons(galleryContainer, 'button[title="Exit fullscreen mode"]');
            }
        }

        if (event.code === "KeyA") {
            clickVisibleButtons(galleryContainer, 'button.to-a');
        }

        if (event.code === "KeyB") {
            clickVisibleButtons(galleryContainer, 'button.to-b');
        }

        if (event.code === "KeyC") {
            if (isCtrl) {
                clickVisibleButtons(galleryContainer, 'button.copy, button[title="Copy"]');
            } else {
                clickVisibleButtons(galleryContainer, 'button.compare');
            }
        }

        if (!event.altKey && isCtrl && event.code === "KeyV") {
            clickVisibleButtons(galleryContainer, 'button.paste');
        }


        if (event.code === "Space") {
            if (galleryVideo && document.activeElement !== galleryVideo) {
                if (galleryVideo.paused) {
                    galleryVideo.play();
                } else {
                    galleryVideo.pause();
                }
                event.preventDefault();
            }
            const audioPlayPauseButton = galleryContainer.querySelector(".play-pause-button");
            if (audioPlayPauseButton) {
                audioPlayPauseButton.click();
                event.preventDefault();
            }
        }

        if (event.code === "KeyE") {
            const forceOpen = isCtrl || event.shiftKey;
            tryOpenEditorFromHotkey(galleryContainer, forceOpen);
        }

        if (event.code === "KeyM") {
            clickVisibleButtons(galleryContainer, ".markdown-toggle input");
            if (galleryVideo) {
                galleryVideo.muted = !galleryVideo.muted;
            }
        }

        if (needVolumeHotkeys) {
            let volumeChanged = false;

            if (event.code === "ArrowUp") {
                let newVolume = galleryVideo.volume * 1.1;
                galleryVideo.volume = Math.min(newVolume, 1.0);
                volumeChanged = true;
            }
            if (event.code === "ArrowDown") {
                let newVolume = galleryVideo.volume * 0.9;
                galleryVideo.volume = Math.max(newVolume, 0.001);
                volumeChanged = true;
            }

            if (volumeChanged) {
                event.preventDefault();
                galleryVideo.classList.add("tmp-show-volume");
                if (galleryVideo.volumeTimeoutId) {
                    clearTimeout(galleryVideo.volumeTimeoutId);
                }
                galleryVideo.volumeTimeoutId = setTimeout(() => {
                    galleryVideo.classList.remove("tmp-show-volume");
                    galleryVideo.volumeTimeoutId = null;
                }, 1500);
            }
        }

        if (event.code === "KeyZ") {
            dispatchSyntheticKey(event, "ArrowLeft", "ArrowLeft");
        }
        if (event.code === "KeyX") {
            dispatchSyntheticKey(event, "ArrowRight", "ArrowRight");
        }

        galleryContainer.querySelector(".thumbnail-item.selected")?.focus();

        if (!inGalleryFullscreen && event.code === "Escape") {
            galleryContainer.querySelector('button[title="Close"]')?.click();
        }

    } else { // not over a gallery
        if (!event.altKey && isCtrl && event.code === "KeyV") {
            querySelectorVisible(document, ".metadata-tab button.paste")?.click();
        }
    }

}, true);


window.addEventListener('paste', (event) => {
    if (activeElementEditable()) {
        return;
    }
    const galleryContainer = getGalleryContainerUnderCursor();
    const metadataPasteButton = querySelectorVisible(document, ".metadata-tab button.paste");
    if (!galleryContainer?.querySelector("button.paste") && !metadataPasteButton) {
        openFileFromPasteEvent(event);
    }
});


navigator?.keyboard?.lock(["Escape"]);

