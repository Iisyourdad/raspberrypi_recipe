#!/bin/bash
# Check if the configuration flag exists.
if [ ! -f /home/tyler/configured.flag ]; then
    # If not configured, load the splash page.
    /bin/chromium-browser --touch-events=enabled --enable-pinch --enable-touch-drag-drop --kiosk --ozone-platform=wayland --start-maximized http://127.0.0.1:8000/splash/
else
    # Otherwise, launch the normal index page.
    /bin/chromium-browser --touch-events=enabled --enable-pinch --enable-touch-drag-drop --kiosk --ozone-platform=wayland --start-maximized http://127.0.0.1:8000/
fi
