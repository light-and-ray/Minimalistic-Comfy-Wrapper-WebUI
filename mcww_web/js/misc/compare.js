
onPageSelected((page) => {
    if (page === "compare") {
        waitForElement("#compareImageA_url textarea", (textareaA) => {
            waitForElement("#compareImageB_url textarea", (textareaB) => {
                if (globalCompareImageA) {
                    textareaA.value = globalCompareImageA;
                    textareaA.dispatchEvent(new Event('input', { bubbles: true }));
                }
                if (globalCompareImageB) {
                    textareaB.value = globalCompareImageB;
                    textareaB.dispatchEvent(new Event('input', { bubbles: true }));
                }
                button = document.querySelector("#compareImagesButton");
                button.click();
            });
        });
    }
});


function openComparePage() {
    selectMainUIPage("compare");
}


var globalCompareImageA = null;
var globalCompareImageB = null;

function swapGlobalImagesAB() {
    const oldA = globalCompareImageA;
    globalCompareImageA = globalCompareImageB;
    globalCompareImageB = oldA;
}


function updateCompareOpacity(opacity) {
    // Create or update a style element in the document head
    let styleElement = document.getElementById('compare-opacity-style');
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'compare-opacity-style';
        document.head.appendChild(styleElement);
    }
    // Set the CSS rule for the second img inside div.slider-wrap
    styleElement.textContent =
        'div.slider-wrap img:nth-child(2) { opacity: ' + opacity + ' !important; }';
}


function downloadCompareComposite() {
    const baseImage = document.querySelector(".compare-image-slider img:not(.fixed)");
    const topImage = document.querySelector(".compare-image-slider img.fixed");
    if (!baseImage || !topImage) {
        return;
    }
    if (!baseImage.complete || !topImage.complete) {
        console.error('One or both images are not fully loaded.');
        return;
    }

    // Get the dimensions of the img element for the top image
    const topImageElementRect = topImage.getBoundingClientRect();
    const topImageElementWidth = topImageElementRect.width;
    const topImageElementHeight = topImageElementRect.height;

    // Get the natural dimensions of the top image
    const topImageNaturalWidth = topImage.naturalWidth;
    const topImageNaturalHeight = topImage.naturalHeight;

    // Calculate aspect ratios
    const topImageElementAspectRatio = topImageElementWidth / topImageElementHeight;
    const topImageNaturalAspectRatio = topImageNaturalWidth / topImageNaturalHeight;

    // Determine the actual width of the image within the img element
    let topImageActualWidth, topImageActualHeight;
    if (topImageNaturalAspectRatio < topImageElementAspectRatio) {
        // Image is centered vertically, height equals element height
        topImageActualHeight = topImageElementHeight;
        topImageActualWidth = topImageActualHeight * topImageNaturalAspectRatio;
    } else {
        // Image is centered horizontally, width equals element width
        topImageActualWidth = topImageElementWidth;
        topImageActualHeight = topImageActualWidth / topImageNaturalAspectRatio;
    }

    // Calculate the start and end percentages of the image within the img element
    const topImageStartPercentage = (topImageElementWidth - topImageActualWidth) / (2 * topImageElementWidth);
    const topImageEndPercentage = 1 - topImageStartPercentage;

    // Get the inset percentage from the clip-path
    const clipPath = window.getComputedStyle(topImage).clipPath;
    // Extract the inset value (assuming format is inset(0px 0px 0px X%)
    const insetMatch = clipPath.match(/inset\(.*?(\d+\.?\d*)%.*?\)/);
    let insetPercentage = 0;
    if (insetMatch) {
        insetPercentage = parseFloat(insetMatch[1]) / 100;
    }

    // Rescale the inset percentage to match the actual image width
    const adjustedInsetPercentage = insetPercentage - topImageStartPercentage;
    const adjustedInsetWidthPercentage = adjustedInsetPercentage / (topImageEndPercentage - topImageStartPercentage);
    // use adjustedInsetWidthPercentage later

    const topImageStyle = window.getComputedStyle(topImage);
    const opacity = parseFloat(topImageStyle.opacity) || 1.0;

    let compositeHeight = null;
    let compositeWidth = null;
    const baseAspect = baseImage.naturalWidth / baseImage.naturalHeight;
    const topAspect = topImage.naturalWidth / topImage.naturalHeight;

    if (baseImage.naturalHeight > topImage.naturalHeight) {
        compositeHeight = baseImage.naturalHeight;
        if (baseAspect >= topAspect) {
            compositeWidth = baseImage.naturalWidth;
        } else {
            compositeWidth = topImage.naturalWidth * (baseImage.naturalHeight / topImage.naturalHeight);
        }
    } else {
        compositeHeight = topImage.naturalHeight;
        if (topAspect >= baseAspect) {
            compositeWidth = topImage.naturalWidth;
        } else {
            compositeWidth = baseImage.naturalWidth * (topImage.naturalHeight / baseImage.naturalHeight);
        }
    }
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = compositeWidth;
    canvas.height = compositeHeight;
    ctx.fillStyle = 'transparent';
    ctx.fillRect(0, 0, compositeWidth, compositeHeight);
    const getDrawParams = (img, areaW, areaH) => {
        const imgRatio = img.naturalWidth / img.naturalHeight;
        let w = areaW;
        let h = areaH;
        let x = 0;
        let y = 0;
        w = areaH * imgRatio;
        x = (areaW - w) / 2; // Center horizontally
        return { x, y, w, h };
    };
    const baseParams = getDrawParams(baseImage, compositeWidth, compositeHeight);
    ctx.drawImage(
        baseImage,
        baseParams.x,
        baseParams.y,
        baseParams.w,
        baseParams.h
    );
    const topParams = getDrawParams(topImage, compositeWidth, compositeHeight);

    // Calculate the visible part of the top image based on adjustedInsetWidthPercentage
    const visibleWidth = topParams.w * (1 - adjustedInsetWidthPercentage);
    const visibleX = topParams.x + (topParams.w * adjustedInsetWidthPercentage);

    // Draw only the visible part of the top image
    ctx.globalAlpha = opacity;
    ctx.drawImage(
        topImage,
        // Source rectangle (crop the top image based on adjustedInsetWidthPercentage)
        topImage.naturalWidth * adjustedInsetWidthPercentage, 0,
        topImage.naturalWidth * (1 - adjustedInsetWidthPercentage), topImage.naturalHeight,
        // Destination rectangle (where to draw the cropped part)
        visibleX, topParams.y,
        visibleWidth, topParams.h
    );
    ctx.globalAlpha = 1.0;
    const dataURL = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataURL;
    const topName = getShortImageName(topImage.src);
    const baseName = getShortImageName(baseImage.src);
    if (topName !== "image" && baseName !== "image") {
        a.download = `composite ${baseName} - ${topName}.png`;
    } else {
        a.download = `composite_image.png`;
    }
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}


