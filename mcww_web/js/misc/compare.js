
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

