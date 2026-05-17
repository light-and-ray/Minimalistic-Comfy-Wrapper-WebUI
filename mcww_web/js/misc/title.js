
class _Title {
    constructor () {
        this._baseTitle = document.title;
        this._progress = null;
        this._page = null;
        this._queueIndicator = null;
        this._selectedTab = {};
        this._selectedProjectWorkflow = null;
        this._selectedQueueWorkflow = null;
        this._openedFileName = null;
        this._mediaSessionMetadata = {
            title: null,
            artist: this._baseTitle,
            artwork: [
                {
                    "src": '/pwa/icon.png',
                    "sizes": "1024x1024",
                    "type": "image/png",
                },
            ],
        };
        this._apply();
        this.blockTitleChange = false;
    }

    setPage(value) {
        this._page = value;
        this._apply();
    }

    setTab(page, value) {
        this._selectedTab[page] = value;
        this._apply();
    }

    setProgress(value) {
        this._progress = value;
        this._apply();
    }

    setQueueIndicator(value) {
        this._queueIndicator = value;
        this._apply();
    }

    setSelectedProjectWorkflow(value) {
        this._selectedProjectWorkflow = value;
        this._apply();
    }

    setSelectedQueueWorkflow(value) {
        this._selectedQueueWorkflow = value;
        this._apply();
    }

    setOpenedFileName(value) {
        this._openedFileName = value;
        this._apply();
    }

    refresh() {
        this._apply();
    }

    _apply() {
        if (this.blockTitleChange) {
            return;
        }
        if (this._page === null) {
            return;
        }
        let mediaSessionTitle = null;
        let newTitle = isInsidePWA() ? "" : this._baseTitle;
        if (this._page === "project" && this._selectedProjectWorkflow) {
            newTitle = newTitle = `${capitalize(this._selectedProjectWorkflow)} – ${newTitle}`;
            mediaSessionTitle = capitalize(this._selectedProjectWorkflow);
        } else if (this._page === "queue" && this._selectedQueueWorkflow) {
            const selectedTab = this._selectedTab[this._page];
            let pageStr = capitalize(this._page);
            pageStr = pageStr.replace(/_/g, ' ');
            newTitle = `${pageStr} – ${capitalize(this._selectedQueueWorkflow)} – ${newTitle}`;
            mediaSessionTitle = capitalize(this._selectedQueueWorkflow);
        } else if (this._page === "fileOpen"){
            let text = "";
            if (this._openedFileName) {
                text = this._openedFileName;
            } else {
                text = "Open file";
            }
            newTitle = `${text} – ${newTitle}`;
            mediaSessionTitle = text;
        } else {
            const selectedTab = this._selectedTab[this._page];
            if (selectedTab) {
                newTitle = `${selectedTab} – ${newTitle}`;
            }
            if (this._page !== "helpers") {
                let pageStr = capitalize(this._page);
                pageStr = pageStr.replace(/_/g, ' ');
                newTitle = `${pageStr} – ${newTitle}`;
            }
            mediaSessionTitle = capitalize(this._page);
        }
        newTitle = removeSuffix(newTitle, " – ");
        if (this._progress) {
            newTitle = `${this._progress} ${newTitle}`;
        }
        if (this._queueIndicator) {
            let text = this._queueIndicator;
            if (isStringNumber(text)) {
                text = `(${text})`
            }
            newTitle = `${text} ${newTitle}`;
        }
        document.title = newTitle;
        this._mediaSessionMetadata.title = mediaSessionTitle;
        if ("mediaSession" in navigator && OPTIONS.titleInMediaSession) {
            navigator.mediaSession.metadata = new MediaMetadata(this._mediaSessionMetadata);
        }

    }
}

