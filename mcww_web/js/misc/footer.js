
function rebuildFooter() {
    const footer = document.querySelector('footer');
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

    let newLinks = [
        { text: "Report an issue", url: "https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI/issues" },
        { text: "MCWW", url: "https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI" },
        { text: "Gradio", url: "https://www.gradio.app/" }
    ];
    if (isSecureContext && 'getDisplayMedia' in window.navigator.mediaDevices) {
        newLinks.push({ button: screenRecorder });
    }
    newLinks = newLinks.concat([
        { text: "ComfyUI", url: "https://www.comfy.org/" },
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
            footer.appendChild(anchor);
        }
        if (index < newLinks.length - 1) {
            const divider = originalDividerTemplate.cloneNode(true);
            footer.appendChild(divider);
        }
    });
    footer.classList.add("mcww-visible");
    footer.appendChild(stopRecording);
}

waitForElement("footer", rebuildFooter);

