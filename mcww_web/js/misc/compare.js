
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


function tryModifyOpacity(difference) {
    const slider = document.querySelector('.opacity-slider input[type="range"]');
    if (!slider) return;
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
}

