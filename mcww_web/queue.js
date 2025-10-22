
function applyMcwwQueueJson() {
    // Find the fieldset containing the radio labels
    const fieldset = document.querySelector('fieldset.mcww-queue-radio');
    if (!fieldset) {
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

        span.classList.add("mcww-hidden");
        label.querySelectorAll('.queue-content').forEach(element => {
            element.remove();
        });

        const key = span.textContent.trim();
        if (key === '-1') {
            label.classList.add('mcww-hidden');
            return;
        } else {
            label.classList.remove('mcww-hidden');
        }

        const data = json[key];
        if (!data) return;

        // Clear the span
        contentDiv = document.createElement('div')
        contentDiv.classList.add("queue-content");
        span.parentElement.appendChild(contentDiv);

        // Add media if present
        if (data.fileUrl) {
            const fileUrl = data.fileUrl.toLowerCase();

            if (fileUrl.endsWith('.jpg') || fileUrl.endsWith('.jpeg') || fileUrl.endsWith('.png') ||
                    fileUrl.endsWith('.gif') || fileUrl.endsWith('.webp') || fileUrl.endsWith('.avif') ||
                    fileUrl.endsWith('.heif') || fileUrl.endsWith('.heic') || fileUrl.endsWith('.jxl')) {
                const img = document.createElement('img');
                img.src = data.fileUrl;
                contentDiv.appendChild(img);
            }
            else if (fileUrl.endsWith('.mp4') || fileUrl.endsWith('.webm')) {
                const video = document.createElement('video');
                video.src = data.fileUrl;
                video.controls = false;
                video.autoplay = true;
                video.loop = true;
                contentDiv.appendChild(video);
            }
        }

        // Add text (wrapped in a div for styling)
        const textDiv = document.createElement('div');
        textDiv.textContent = data.text;
        textDiv.classList.add('mcww-text');
        contentDiv.appendChild(textDiv);

        // Add ID in the bottom right corner
        const idDiv = document.createElement('div');
        idDiv.textContent = data.id;
        idDiv.classList.add('mcww-id');
        contentDiv.appendChild(idDiv);

        // Add type as a class to the label
        label.classList.remove("in_progress", "queued", "complete", "error");
        if (data.type) {
            label.classList.add(data.type);
        }
    });
    fieldset.classList.remove('mcww-hidden');
}

function initiallyApplyMcwwQueueUIJson() {
    const fieldset = document.querySelector('fieldset.mcww-queue-radio');
    const textarea = document.querySelector('.mcww-queue-json textarea');
    if (!fieldset || !textarea) {
        return;
    }

    if (fieldset.dataset.mcwwQueueJsonInitiallyApplied === 'true') {
        return;
    }
    applyMcwwQueueJson();

    fieldset.dataset.mcwwQueueJsonInitiallyApplied = 'true';
}

onUiUpdate(initiallyApplyMcwwQueueUIJson);

