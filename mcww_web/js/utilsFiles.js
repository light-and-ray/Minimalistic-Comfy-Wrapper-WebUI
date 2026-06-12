
function isImageUrl(url) {
    const lowerCaseUrl = url.toLowerCase();
    return MCWW.IMAGE_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}

function isVideoUrl(url) {
    const lowerCaseUrl = url.toLowerCase();
    return MCWW.VIDEO_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}

function isAudioUrl(url) {
    const lowerCaseUrl = url.toLowerCase();
    return MCWW.AUDIO_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}

function isModel3DUrl(url) {
    const lowerCaseUrl = url.toLowerCase();
    return MCWW.MODEL_3D_EXTENSIONS.some(ext => lowerCaseUrl.endsWith(ext));
}

function getBasename(url) {
    const basename = url.substring(url.lastIndexOf('/') + 1);
    return decodeURIComponent(basename);
}

function removeImageExtension(string) {
    const lowerCaseString = string.toLowerCase();

    for (const ext of MCWW.IMAGE_EXTENSIONS) {
        if (lowerCaseString.endsWith(ext)) {
            const extLength = ext.length + 1;
            return string.slice(0, -extLength);
        }
    }
    return string;
}

function getShortImageName(url) {
    return removeImageExtension(getBasename(decodeURIComponent(url))).slice(0, 50)
}


async function getBlobHash(blob, length = null) {
    const arrayBuffer = await blob.arrayBuffer();
    let hashHex = '';
    if (crypto?.subtle) {
        const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        hashHex = hashArray
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    } else {
        hashHex = simpleChecksum(arrayBuffer);
    }

    return length ? hashHex.slice(0, length) : hashHex;
}


async function fileUrlToFile(fileUrl) {
    try {
        const response = await fetch(fileUrl);
        if (!response.ok) throw new Error(`Failed to fetch file: ${response.statusText}`);
        let blob = await response.blob();
        let fileName;
        if (fileUrl.startsWith('blob:')) {
            let tmpBlobFileName = getSessionStorageVariable("tmpBlobFileName");
            if (tmpBlobFileName) {
                fileName = tmpBlobFileName;
            } else {
                let extension = blob.type.split('/')[1] || 'bin';
                const extensionMap = {
                    'mpeg': 'mp3',
                    'quicklime': 'mov',
                    'jpeg': 'jpg',
                    'x-msfido': 'avi',
                };
                extension = extensionMap[extension] || extension;
                fileName = `file_${await getBlobHash(blob, 20)}.${extension}`;
            }
        } else {
            fileName = getBasename(fileUrl);
        }
        if (isImageUrl(fileUrl) && !blob.type.startsWith("image/")) {
            console.log(`Image ${fileUrl} will be converted to png, because` +
                ` fetched blob doesn't have an image type`);
            blob = await convertBlobToPng(blob);
        }
        return new File([blob], fileName, { type: blob.type });
    } catch (error) {
        console.error("Failed on fileUrlToFile:", error);
        throw error;
    }
}


function canvasToImageFile(canvas) {
    return new Promise((resolve, reject) => {
        canvas.toBlob((blob) => {
            if (blob) {
                const timestamp = new Date().getTime();
                const file = new File([blob], `tmp-${timestamp}.png`, { type: "image/png" });
                resolve(file);
            } else {
                reject(new Error("Failed to create blob from canvas."));
            }
        }, 'image/png', 1.0);
    });
}


async function awaitImageLoad(imgElement, timeout = 5000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
        if (imgElement.complete && imgElement.naturalWidth !== 0) {
            return imgElement;
        }
        await sleep(50);
    }

    throw new Error('Image loading timed out');
}


function convertBlobToPng(blob) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        const url = URL.createObjectURL(blob);

        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);

            canvas.toBlob((pngBlob) => {
                URL.revokeObjectURL(url);
                if (pngBlob) resolve(pngBlob);
                else reject(new Error('Canvas to Blob conversion failed'));
            }, 'image/png');
        };

        img.onerror = () => {
            URL.revokeObjectURL(url);
            reject(new Error('Failed to load image for conversion'));
        };

        img.src = url;
    });
}

function createObjectURLWithAutoRevoke(blob, revokeTime=60000) {
    const url = window.URL.createObjectURL(blob);
    setTimeout(() => {
        window.URL.revokeObjectURL(url);
    }, revokeTime);
    return url;
}

function downloadFileByUrl(url) {
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}


function downloadTextAsFile(text, fileName) {
    if (!text) {
        grWarning(`File "${fileName}" is empty`);
        return;
    }
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    showDownloadingAlert();
}
