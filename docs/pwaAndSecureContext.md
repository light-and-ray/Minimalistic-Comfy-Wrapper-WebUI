## Install as PWA on desktop

If you use MCWW on localhost (127.0.0.1), installing PWA should be easy - just click a button in address panel, or in the management tab, and then click "Install"

![](/docs/assets/pwaAndSecureContext/desktop.png)

Features:
- Shortcuts on desktop and start menu
- No browser UI
- No context menu or text selection on elements where it's not supposed to be
- Offline placeholder

If you see "Not supported. Read here for details", the possible reasons are:
- Connection is not secure. If your UI is on localhost be sure the address is not 0.0.0.0. Use 127.0.0.1 instead. If it's on another PC, and scheme HTTP (not HTTPS) read below how to acquire secure connection without certificates or tunnels
- Browser doesn't support it. Firefox desktop doesn't support PWAs, other browsers should support

## Share over local network

You can get access to ComfyUI and Minimalistic over local network (e.g. from phone or from a laptop). To do this you need to add `--listen` flag in ComfyUI. In standalone server mode it should be `GRADIO_SERVER_NAME="0.0.0.0"` environment variable. It will be available in the same network. To open it use server's ip address and port (you can find it in a task manager)

In local network you will lose some features due to insecure HTTP context. You can get them back using the instruction below

## Secure context

Secure context is localhost, 127.0.0.1, or HTTPS. In this context MCWW supports additional features:
- Web camera inside image upload component
- Screen recorder
- PWA (Install as an app)

### Get secure context on local network

You can get secure context on chromium-based browsers (e.g. [Cromite](https://github.com/uazo/cromite) in this guide). Open page with address `chrome://flags`, search for "insecure", enter your address here and select "enabled". Then you need to restart the app. It can not be restarted after closing and reopening, so you need to force stop it inside android's app info page

<img src="/docs/assets/pwaAndSecureContext/secureContext.png" height="600"/>

On PC you will have an annoying message on startup, here is the solutions how to hide it: https://github.com/uazo/cromite/issues/2605

![](/docs/assets/pwaAndSecureContext/desktopWarning.png)

## Install as an app (PWA)

You can use PWA to install this app on your phone. If you use it over local network you need to get secure context to the app (see above). Follow steps in the picture

<img src="/docs/assets/pwaAndSecureContext/pwa.png" height="600"/>

<img src="/docs/assets/pwaAndSecureContext/homeScreen.jpg" width="300"/>

It's here! Now you can use it in separate window instead of browser's tab


