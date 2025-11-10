
const selectedRowSelector = ".mcww-loras-table td.cell-selected:not(.fixed)";

function fixSelectedRow(selectedRow) {
    if (selectedRow) {
        const newSelectedRow = selectedRow.cloneNode(true);
        selectedRow.parentNode.replaceChild(newSelectedRow, selectedRow);
        newSelectedRow.classList.add("fixed");
    }
    waitForElement(selectedRowSelector, fixSelectedRow);
}

fixSelectedRow(null);


