
class McwwMenuBase {
    constructor(event, options = {}) {
        this.event = event;
        this.options = {
            relaxed: false,
            className: 'mcww-menu',
            containerSelector: 'main',
            ...options
        };
        this.closeHandler = null;
        this.removeExisting();

        this.menu = document.createElement('div');
        this.menu.classList.add('mcww-menu', this.options.className);
    }


    createItem(iconHtml, text, action) {
        const item = document.createElement('div');
        item.className = 'menu-item';

        const iconSpan = document.createElement('span');
        iconSpan.className = 'icon';
        iconSpan.innerHTML = iconHtml;

        const textSpan = document.createElement('span');
        textSpan.className = 'text';
        textSpan.textContent = text || "Action";

        item.appendChild(iconSpan);
        item.appendChild(textSpan);

        item.addEventListener('click', (e) => {
            e.stopPropagation();
            action();
            this.destroy();
        });
        return item;
    }


    render() {
        const container = document.querySelector(this.options.containerSelector) || document.body;
        container.appendChild(this.menu);

        const viewport = window.visualViewport || {
            scale: 1,
            offsetLeft: 0,
            offsetTop: 0,
            width: window.innerWidth,
            height: window.innerHeight
        };
        let scale = 1 / viewport.scale;
        if (this.event.pointerType === "touch") {
            scale *= 1.2;
        }

        const { clientX: x, clientY: y } = this.event;
        let { width, height } = getFullElementSize(this.menu);
        height *= scale;
        width *= scale;

        const minX = viewport.offsetLeft;
        const maxX = viewport.offsetLeft + viewport.width;
        const minY = viewport.offsetTop;
        const maxY = viewport.offsetTop + viewport.height;

        let posX, posY;

        // Horizontal Logic (Standard Flip)
        // We check against the actual right edge of the viewport (maxX)
        posX = (x + width > maxX) ? x - width : x;
        posX = clamp(posX, minX, maxX - width);

        // Vertical Logic: Relaxed vs Strict
        if (this.options.relaxed) {
            // Pull toward center based on cursor position relative to the visible viewport
            const bias = (y - minY) / viewport.height;
            posY = y - (height * bias);
        } else {
            // Standard Flip checking against bottom edge (maxY)
            posY = (y + height > maxY) ? y - height : y;
        }
        posY = clamp(posY, minY, maxY - height);

        this.menu.style.left = `${posX}px`;
        this.menu.style.top = `${posY}px`;
        this.menu.style.transform = `scale(${scale})`;
        this.menu.style.maxHeight = `calc(${viewport.height * 0.8}px / ${scale})`;

        this.setupListeners();
    }


    setupListeners() {
        this.closeHandler = (e) => {
            if (e.type === 'keydown') {
                const modifiers = ['Alt', 'Control', 'Shift', 'Meta'];
                if (modifiers.includes(e.key)) {
                    return;
                }
            }
            if (e.target instanceof VisualViewport || !this.menu.contains(e.target)) {
                this.destroy();
            }
        };
        const opts = { capture: true };
        ['pointerdown', 'keydown', 'scroll'].forEach(type => {
            document.addEventListener(type, this.closeHandler, opts);
        });
        if (window.visualViewport) {
            ['resize', 'scroll'].forEach(type => {
                window.visualViewport.addEventListener(type, this.closeHandler, opts);
            });
        }
    }

    removeExisting() {
        const old = document.querySelector(`.${this.options.className}`);
        if (old) old.remove();
    }

    destroy() {
        this.removeExisting();
        if (this.closeHandler) {
            const opts = { capture: true };
            ['pointerdown', 'keydown', 'scroll'].forEach(type => {
                document.removeEventListener(type, this.closeHandler, opts);
            });
            if (window.visualViewport) {
                ['resize', 'scroll'].forEach(type => {
                    window.visualViewport.removeEventListener(type, this.closeHandler, opts);
                });
            }
            this.closeHandler = null;
        }
    }
}

