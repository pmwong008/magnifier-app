import os
import cv2
import subprocess
from gpiozero import Button
from tkinter import Tk, Button as TkButton
import logging

logger = logging.getLogger("magnifier")

# --- GPIO pins ---
PIN_ZOOM_IN = 17
PIN_ZOOM_OUT = 27
PIN_QUIT = 22
PIN_WAKE = 23

def set_display_timeout(seconds=1200):  # 20 minutes
    subprocess.run(["xset", "s", str(seconds)])
    subprocess.run(["xset", "dpms", "0", "0", str(seconds)])
    logger.info("Display timeout set to %d seconds", seconds)

def run_magnifier(screen_width=1280):
    camera_type, cam = get_camera_source()
    zoom_factor = 1.0
    running = True

    def adjust_zoom(delta):
        nonlocal zoom_factor
        zoom_factor = max(1.0, zoom_factor + delta)
        logger.info("Zoom adjusted: %.1fx", zoom_factor)

    def stop_running():
        nonlocal running
        logger.info("Quit triggered")
        running = False

    def wake_screen():
        logger.info("Wake Up button pressed")
        subprocess.run(["xset", "dpms", "force", "on"])

    # --- Bind controls depending on ENV ---
    if os.getenv("MAGNIFIER_ENV") == "PROD":
        logger.info("Binding GPIO buttons")
        btn_zoom_in = Button(PIN_ZOOM_IN, pull_up=True)
        btn_zoom_out = Button(PIN_ZOOM_OUT, pull_up=True)
        btn_quit = Button(PIN_QUIT, pull_up=True)
        btn_wake = Button(PIN_WAKE, pull_up=True)

        btn_zoom_in.when_pressed = lambda: adjust_zoom(0.1)
        btn_zoom_out.when_pressed = lambda: adjust_zoom(-0.1)
        btn_quit.when_pressed = stop_running
        btn_wake.when_pressed = wake_screen

        set_display_timeout(1200)  # 20 minutes
    else:
        logger.info("Binding Tkinter buttons (DEV mode)")
        root = Tk()
        TkButton(root, text="Zoom In", command=lambda: adjust_zoom(0.1)).pack()
        TkButton(root, text="Zoom Out", command=lambda: adjust_zoom(-0.1)).pack()
        TkButton(root, text="Quit", command=stop_running).pack()
        TkButton(root, text="Wake Up", command=wake_screen).pack()

    # --- Main loop ---
    while running:
        if camera_type == "pi":
            frame = cam.capture_array()
        else:
            ret, frame = cam.read()
            if not ret:
                logger.error("Failed to capture frame")
                break

        h, w = frame.shape[:2]
        if zoom_factor > 1.0:
            new_w = int(w / zoom_factor)
            new_h = int(h / zoom_factor)
            x1 = (w - new_w) // 2
            y1 = (h - new_h) // 2
            frame = frame[y1:y1+new_h, x1:x1+new_w]

        height = int(frame.shape[0] * (screen_width / frame.shape[1]))
        frame = cv2.resize(frame, (screen_width, height))
        cv2.imshow("Magnifier", frame)
        cv2.resizeWindow("Magnifier", screen_width, height)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_running()

    # Cleanup
    if camera_type == "pi":
        cam.stop()
    else:
        cam.release()
    cv2.destroyAllWindows()
    logger.info("Magnifier closed")
