
function applyMcwwQueueJson() {
    // Find the fieldset containing the radio labels
    const fieldset = document.querySelector('fieldset.mcww-queue-radio');
    if (!fieldset) {
        return;
    }

    // Check if already applied
    if (fieldset.dataset.mcwwQueueJsonApplied === 'true') {
        return;
    }

    // Find the textarea containing the JSON
    const textarea = document.querySelector('.mcww-queue-json textarea');
    if (!textarea) {
        console.error('No .mcww-queue-json textarea found');
        return;
    }

    let json;
    try {
        json = JSON.parse(textarea.value);
    } catch (e) {
        console.error('Invalid JSON in .mcww-queue-json textarea', e);
        return;
    }

    // Process each label in the fieldset
    const labels = fieldset.querySelectorAll('label');
    labels.forEach(label => {
        const span = label.querySelector('span');
        if (!span) return;

        const key = span.textContent.trim();
        if (key === '-1') {
            label.classList.add('mcww-hidden');
            return;
        }

        const data = json[key];
        if (!data) return;

        // Clear the span
        span.innerHTML = '';

        // Add image if present
        if (data.image) {
            const img = document.createElement('img');
            img.src = data.image;
            span.appendChild(img);
        }

        // Add text (wrapped in a div for styling)
        const textDiv = document.createElement('div');
        textDiv.textContent = data.text;
        textDiv.classList.add('mcww-text');
        span.appendChild(textDiv);

        // Add ID in the bottom right corner
        const idSpan = document.createElement('span');
        idSpan.textContent = data.id;
        idSpan.classList.add('mcww-id');
        span.appendChild(idSpan);

        // Add type as a class to the label
        if (data.type) {
            label.classList.add(data.type);
        }
    });

    // Mark as applied
    fieldset.dataset.mcwwQueueJsonApplied = 'true';
}


onUiUpdate(applyMcwwQueueJson);


// onUiUpdate(() => {
//     const selected = document.querySelector(".mcww-queue-radio label.selected");
//     workflow = document.querySelector(".queue-ui .active-workflow-ui");
//     if (selected && workflow && !workflow.dataset.mcww_scrolled) {
//         workflow.dataset.mcww_scrolled = 'true';
//         setTimeout(() => {selected.scrollIntoView({
//                 behavior: 'smooth',
//                 block: 'center'
//             });
//         }, 500);
//     }
// });
