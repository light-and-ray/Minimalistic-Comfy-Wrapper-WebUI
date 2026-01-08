
function getSelectedMainUIPage() {
    return document.querySelector('.mcww-main-ui-page label.selected span')?.textContent.trim();
}

function getSelectedMainUIPageFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page_') || 'project';
    return page;
}


function _selectMainUiPageRadio(page) {
    const container = document.querySelector('.mcww-main-ui-page');
    if (!container) {
        console.error('Container ".mcww-main-ui-page" not found.');
        return;
    }

    const labels = container.querySelectorAll('label');
    if (labels.length === 0) {
        console.error('No labels found inside ".mcww-main-ui-page".');
        return;
    }

    let found = false;
    labels.forEach(label => {
        const span = label.querySelector('span');
        if (span && span.textContent.trim() === page) {
            const input = label.querySelector('input');
            if (input) {
                input.click();
                found = true;
            }
        }
    });

    if (!found) {
        console.error(`No label with span containing "${page}" found.`);
    }
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


function selectMainUIPage(page) {
    if (getSelectedMainUIPage() === page) {
        grWarning("JS: selectMainUIPage called for the same page");
        if (page === "project") {
            grError("And page is project");
        }
        _selectMainUiPageRadio("project");
    }
    _selectMainUiPageRadio(page);
    executeCallbacks(pageSelectedCallbacks, page);
    if (page !== getSelectedMainUIPageFromUrl()) {
        pushState({triggered: "selectedPage"}, getUrlForNewPage(page));
    }
}


function _deleteUnwantedPageArgumentIfExists() {
    const url = new URL(window.location.href);
    const unwantedPages = ['compare', 'presets', 'image editor'];
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
        // Main ui page from "mcww-main-ui-page" on ui load must always be "project",
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
