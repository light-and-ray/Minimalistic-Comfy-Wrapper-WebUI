
var g_selected_main_ui_page = "init";

function getSelectedMainUIPage() {
    return g_selected_main_ui_page;
}

function getSelectedMainUIPageFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page_') || 'project';
    return page;
}


function getUrlForNewPage(page) {
    const url = new URL(window.location.href);
    if (page !== "project") {
        url.searchParams.set('page_', page);
    } else {
        url.searchParams.delete('page_');
    }
    return url.toString();
}


function _selectMainUiPageInner(page) {
    const uis = document.querySelectorAll(".mcww-page-ui");
    for (const ui of uis) {
        if (ui.classList.contains(page)) {
            ui.classList.add('mcww-visible');
        } else {
            ui.classList.remove('mcww-visible');
        }
    }
    g_selected_main_ui_page = page;
}

var blockPageChange = false;

function selectMainUIPage(page) {
    if (blockPageChange) {
        return;
    }
    if (getSelectedMainUIPage() === page) {
        grWarning("JS: selectMainUIPage called for the same page");
        if (page === "init") {
            grError("And page is init");
        }
        _selectMainUiPageInner("project");
    }
    _selectMainUiPageInner(page);
    executeCallbacks(pageSelectedCallbacks, page);
    if (page !== getSelectedMainUIPageFromUrl()) {
        pushState({triggered: "selectedPage"}, getUrlForNewPage(page));
    }
}


function _deleteUnwantedPageArgumentIfExists() {
    const url = new URL(window.location.href);
    const unwantedPages = ['compare', 'presets', 'image_editor'];
    const currentPage = url.searchParams.get('page_');
    if (currentPage && unwantedPages.indexOf(currentPage) !== -1) {
        url.searchParams.delete('page_');
        replaceState({}, url);
    }
}


onUiLoaded(() => {
    _deleteUnwantedPageArgumentIfExists();
    checkSameAppIdOnUiLoaded();
    if (getSelectedMainUIPage() !== "init") {
        // this is possible on mobile phone where browser partially unloads the page
        // Main ui page from "mcww-main-ui-page" on ui load must always be "init",
        // it's hardcoded in python definition of this object
        reloadPage();
    }
    selectMainUIPage(getSelectedMainUIPageFromUrl());
});


onPopState(()=> {
    if (getSelectedMainUIPage() != getSelectedMainUIPageFromUrl()) {
        selectMainUIPage(getSelectedMainUIPageFromUrl());
    }
});


onPageSelected((page) => {
    if (page === "project") {
        TITLE.setPage(null);
    } else {
        TITLE.setPage(page);
    }
});


var wolf3dEnabled = false;
onPageSelected((page) => {
    if (page === "wolf3d") {
        wolf3dEnabled = true;
        document.querySelector(".enable-wold-3d").click();
    } else if (wolf3dEnabled) {
        wolf3dEnabled = false;
        document.querySelector(".disable-wold-3d").click();
    }
});


function updateSelectedWorkflowTitle() {
    if (!TITLE) {
        setTimeout(updateSelectedWorkflowTitle, 100);
    } else {
        const setWorkflow = () => {
            waitForElement(".workflows-radio label.selected span", (span) => {
                TITLE.setSelectedWorkflow(span.textContent);
            });
        };
        if (getSelectedMainUIPage() !== "project") {
            const onPageSelectedCallback = (page) => {
                if (page === "project") {
                    setWorkflow();
                    const index = pageSelectedCallbacks.indexOf(onPageSelectedCallback);
                    if (index !== -1) {
                        pageSelectedCallbacks.slice(index, 1);
                    }
                }
            }
            onPageSelected(onPageSelectedCallback);
        } else {
            setWorkflow();
        }
    }
}
