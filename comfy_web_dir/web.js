(function() {
    const ROUTE = "/my_extension/get_port";
    const CONTAINER_SELECTOR = ".side-tool-bar-container";
    const BUTTON_ID = "my-extension-open-service-btn";

    async function fetchPort() {
        const resp = await fetch(ROUTE, { cache: "no-store" });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        if (!data || typeof data.port === "undefined") throw new Error("invalid response");
        return data.port;
    }

    function buildLink(port) {
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
        const btn = document.createElement("button");
        btn.id = BUTTON_ID;
        btn.textContent = "My";
        btn.addEventListener("click", (e) => { e.preventDefault(); window.open(link, "_blank"); });
        btn.title = link;
        btn.setAttribute('class', "p-button p-component p-button-icon-only p-button-text side-bar-button p-button-secondary");
        return btn;
    }

    function waitForContainer(timeoutMs = 1000) {
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
        try {
            const port = await fetchPort();
            const link = buildLink(port);
            const container = await waitForContainer();
            const btn = createButton(link);
            if (!container.querySelector(`#${BUTTON_ID}`)) container.appendChild(btn);
            console.log("[my_extension] Sidebar button added ->", link);
        } catch (err) {
            console.warn("[my_extension] Button init failed:", err);
        }
    }

    if (typeof window !== "undefined") {
        window.addEventListener("comfy-ui-loaded", () => init(), { once: true });
        window.addEventListener("DOMContentLoaded", () => setTimeout(init, 200), { once: true });
        // final fallback in case events are not fired
        setTimeout(() => { if (!document.getElementById(BUTTON_ID)) init(); }, 1000);
    }
})();
