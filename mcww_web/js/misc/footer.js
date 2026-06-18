
async function rebuildFooter() {
    const footer = document.querySelector('footer');
    try {
        footer.querySelector("button.settings").click();
        await _selectEnglish();
        document.querySelector("div.api-docs>div.backdrop").click();
    } catch (error) {
        console.error("Unexpected error in selecting english in footer:", error);
        grError("Unexpected error in selecting english in footer");
    }

    if (!footer) {
        console.error("Footer element not found.");
        return;
    }

    const originalLinkTemplate = footer.querySelector('a.built-with');
    const originalDividerTemplate = footer.querySelector('div.divider');

    if (!originalLinkTemplate || !originalDividerTemplate) {
        console.error("Failed to find original template elements (a.built-with or div.divider) for copying.");
        return;
    }

    const screenRecorder = footer.querySelector("button.settings");
    screenRecorder.innerHTML = "Screen recorder";
    const stopRecording = footer.querySelector("button.record");

    const reloadButton = screenRecorder.cloneNode(false);
    reloadButton.classList.add("mcww-reload-ui-button");
    reloadButton.onclick = async () => {
        try {
            await doSaveStates();
        } finally {
            reloadPage();
        }
    };
    reloadButton.innerHTML = "Reload";

    const fullscreenButton = screenRecorder.cloneNode(false);
    fullscreenButton.onclick = toggleUIFullScreen;
    const setFullscreenButtonText = () => {
        if (isUIInFullscreen()) {
            fullscreenButton.innerHTML = "Exit fullscreen";
        } else {
            fullscreenButton.innerHTML = "Fullscreen";
        }
    };
    setFullscreenButtonText();
    window.matchMedia('(display-mode: fullscreen)').addEventListener('change', setFullscreenButtonText);
    window.document.addEventListener('fullscreenchange', setFullscreenButtonText);

    let newLinks = [ ];
    if (!OPTIONS.hideHomepagesInFooter) {
        newLinks = newLinks.concat([
            { text: "Report an issue", url: "https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI/issues" },
            { text: "MCWW", url: "https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI" },
            { text: "Gradio", url: "https://www.gradio.app/" },
            { text: "ComfyUI", url: "https://www.comfy.org/" },
        ]);
    }
    newLinks = newLinks.concat([
        { button: fullscreenButton},
    ]);
    if (isSecureContext && 'getDisplayMedia' in window.navigator.mediaDevices) {
        newLinks.push({ button: screenRecorder });
    }
    newLinks = newLinks.concat([
        { button: reloadButton },
        { text: "Open ComfyUI", url: COMFY_ADDRESS },
    ]);

    footer.innerHTML = '';

    newLinks.forEach((linkData, index) => {
        if (linkData?.button) {
            footer.appendChild(linkData.button);
        } else {
            const anchor = originalLinkTemplate.cloneNode(true);
            anchor.href = linkData.url;
            anchor.textContent = linkData.text;
            if (linkData.target) {
                anchor.target = linkData.target;
            }
            footer.appendChild(anchor);
        }
        if (index < newLinks.length - 1) {
            const divider = originalDividerTemplate.cloneNode(true);
            footer.appendChild(divider);
        }
    });
    footer.classList.add("mcww-visible");
    footer.appendChild(stopRecording);
    addOnResizeCallback(footer, () => {
        const footerHeight = getFullElementSize(footer).height;
        document.documentElement.style.setProperty('--footer-height', `${footerHeight}px`);
    });
}

waitForElement(document, "footer", rebuildFooter);

async function _selectEnglish() {
    const input = await waitForElementAsync(document, 'input[aria-label="Language"]');
    input.focus();

    const languageItemSelector = '.banner-wrap ul.options>li.item';
    await waitForElementAsync(document, languageItemSelector);
    const items = document.querySelectorAll(languageItemSelector);

    for (const item of items) {
        if (item.textContent.toLowerCase().includes("english")) {
            // 1. Get the element's bounding box relative to the viewport
            const rect = item.getBoundingClientRect();

            // 2. Calculate the center X and Y coordinates
            const clientX = rect.left + rect.width / 2;
            const clientY = rect.top + rect.height / 2;

            // 3. Pass the coordinates into the MouseEvent options
            const mouseDownEvent = new MouseEvent('mousedown', {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: clientX,
                clientY: clientY,
                screenX: window.screenX + clientX, // Position relative to the physical screen
                screenY: window.screenY + clientY
            });

            // 4. Dispatch the event
            item.dispatchEvent(mouseDownEvent);

            break;
        }
    }
}


