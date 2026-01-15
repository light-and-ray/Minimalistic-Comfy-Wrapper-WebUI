(function() {
    const AVAILABLE_AT_ROUTE = "/mcww/available_at";
    const LOGO_ROUTE = "/mcww/get_logo";
    const CONTAINER_SELECTOR = ".side-tool-bar-container";
    const BUTTON_ID = "mcww-open-service-btn";

    async function fetchAvailableAt() {
        const resp = await fetch(AVAILABLE_AT_ROUTE, { cache: "no-store" });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        return data;
    }

    function buildLocalLink(port) {
        const protocol = window.location.protocol.replace(":", "");
        let hostname = window.location.hostname;
        if (hostname.includes(":")) hostname = `[${hostname}]`; // IPv6-safe
        return `${protocol}://${hostname}:${port}`;
    }

    function createButton(link) {
        const existing = document.getElementById(BUTTON_ID);
        if (existing) {
            existing.onclick = (e) => { e.preventDefault(); window.open(link, "_blank"); };
            existing.title = link;
            return existing;
        }
        const btn = document.createElement("a");
        btn.id = BUTTON_ID;
        btn.textContent = "Mc";
        btn.href = link;
        btn.target = "_blank";
        btn.title = link;
        btn.setAttribute('class', "p-button p-component p-button-icon-only p-button-text side-bar-button p-button-secondary");
        return btn;
    }

    async function fetchLogo() {
        const resp = await fetch(LOGO_ROUTE, { cache: "force-cache" });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        if (!data?.logo) throw new Error("invalid response");
        return data.logo;
    }


    async function createAndDecorateButton(link) {
        const btn = createButton(link);
        try {
            const svgString = await fetchLogo();
            btn.textContent = "";
            btn.innerHTML = svgString;

        } catch (error) {
            console.error("Failed to fetch or insert logo:", error);
        }
        return btn;
    }


    function injectButtonStyles() {
        const styleId = 'mcww-logo-styles';
        if (document.getElementById(styleId)) return; // Avoid re-injecting

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            #${BUTTON_ID} svg {
                aspect-ratio: 1 / 1;
                width: 1.25rem;
                height: 1.25rem;
                display: block;
                .mcww-logo-svg {
                    fill: var(--p-button-text-secondary-color);
                }
                .bg-square {
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }


    function waitForContainer() {
        const timeoutMs = 10000;
        const start = Date.now();
        return new Promise((resolve, reject) => {
            const tryFind = () => document.querySelector(CONTAINER_SELECTOR);
            const found = tryFind();
            if (found) return resolve(found);
            const poll = setInterval(() => {
                const el = tryFind();
                if (el) {
                    clearInterval(poll);
                    resolve(el);
                } else if (Date.now() - start > timeoutMs) {
                    clearInterval(poll);
                    reject(new Error("timeout waiting for sidebar container"));
                }
            }, 200);
        });
    }


    async function init() {
        injectButtonStyles();

        try {
            const availableAt = await fetchAvailableAt();
            let link = "";
            if (availableAt?.shareUrl) {
                link = availableAt.shareUrl;
            } else {
                link = buildLocalLink(availableAt.port);
            }
            const container = await waitForContainer();
            const btn = await createAndDecorateButton(link);
            if (!container.querySelector(`#${BUTTON_ID}`)) container.appendChild(btn);
            console.log("[mcww] Sidebar button added ->", link);
        } catch (err) {
            console.warn("[mcww] Button init failed:", err);
        }
    }


    if (typeof window !== "undefined") {
        window.addEventListener("comfy-ui-loaded", () => init(), { once: true });
        window.addEventListener("DOMContentLoaded", () => setTimeout(init, 200), { once: true });
        setTimeout(() => { if (!document.getElementById(BUTTON_ID)) init(); }, 1000);
    }
})();
