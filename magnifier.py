import tkinter as tk
import cv2
import os
import logging
from logging.handlers import RotatingFileHandler

# import gpiozero
# from gpiozero.pins.rpigpio import RPiGPIOPinFactory
# gpiozero.Device.pin_factory = RPiGPIOPinFactory()

from gpiozero import Button

# --- Environment flag ---
ENV_MODE = os.getenv("MAGNIFIER_ENV", "DEV")  # default to DEV if not set

if ENV_MODE.upper() == "DEV":
    handler = RotatingFileHandler("magnifier.log", maxBytes=500000, backupCount=3)    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(), handler]  # console + rotating file
    )
else:  # PROD mode
    logging.basicConfig(
        level=logging.ERROR,  # only show errors
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler()]  # console only, no file writes
    )

logger = logging.getLogger("magnifier")

zoom_factor = 1.0

# --- Control functions ---
def adjust_zoom(delta):
    global zoom_factor
    zoom_factor = max(1.0, zoom_factor + delta)
    logger.info("Zoom adjusted: %.1fx", zoom_factor)

def wake_screen():
    logger.info("Wake screen triggered")

def quit_app():
    logger.info("Quit requested")
    cv2.destroyAllWindows()
    exit()

# --- GPIO setup (PROD only) ---
def setup_gpio_controls():
    btn_zoom_in  = Button(17, pull_up=True)
    btn_zoom_out = Button(27, pull_up=True)
    btn_quit     = Button(22, pull_up=True)
    btn_wake     = Button(23, pull_up=True)

    btn_zoom_in.when_pressed  = lambda: adjust_zoom(+0.1)
    btn_zoom_out.when_pressed = lambda: adjust_zoom(-0.1)
    btn_quit.when_pressed     = quit_app
    btn_wake.when_pressed     = wake_screen

    logger.info("GPIO buttons initialized")

# --- Camera source abstraction ---
def get_camera_source():
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
        picam2.start()
        logger.info("Using Pi Camera via Picamera2")
        return ("pi", picam2)
    except Exception:
        logger.warning("Pi Camera not available, falling back to USB webcam")
        cap = cv2.VideoCapture(0)
        return ("usb", cap)

# --- Magnifier loop ---
def run_magnifier(screen_width=1280):
    camera_type, cam = get_camera_source()
    global zoom_factor
    running = True
    logger.info("Magnifier started with width %d", screen_width)
    
    while running:
        if camera_type == "pi":
            frame = cam.capture_array()
        else:
            ret, frame = cam.read()
            if not ret:
                logger.error("Failed to capture frame from PiCamera/webcam")
                break

        h, w = frame.shape[:2]

        # --- Apply zoom by cropping ---
        if zoom_factor > 1.0:
            new_w = int(w / zoom_factor)
            new_h = int(h / zoom_factor)
            x1 = (w - new_w) // 2
            y1 = (h - new_h) // 2
            frame = frame[y1:y1+new_h, x1:x1+new_w]
        
        # --- Resize to chosen screen width ---
        height = int(frame.shape[0] * (screen_width / frame.shape[1]))
        frame = cv2.resize(frame, (screen_width, height))

        # Show the frame in OpenCV window
        cv2.imshow("Magnifier", frame)
        cv2.resizeWindow("Magnifier", screen_width, height)

        # --- Keyboard controls ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            quit_app()
        elif key == ord('+') or key == ord('i'):
            adjust_zoom(+0.1)
        elif key == ord('-') or key == ord('o'):
            adjust_zoom(-0.1)
        elif key == ord('w'):
            wake_screen()
            
    if camera_type == "pi":
        cam.stop()
    else:
        cam.release()
    cv2.destroyAllWindows()
    logger.info("Magnifier closed")    

# --- DEV launch (Tkinter) ---
def launch_dev():
    root = tk.Tk()
    root.title("Magnifier Setup")

    tk.Label(root, text="Choose screen width:").pack(pady=10)

    tk.Button(root, text="Small (640)",
              command=lambda: (root.quit(), root.destroy(), run_magnifier(640))).pack()
    tk.Button(root, text="Medium (800)",
              command=lambda: (root.quit(), root.destroy(), run_magnifier(800))).pack()
    tk.Button(root, text="Large (1280)",
              command=lambda: (root.quit(), root.destroy(), run_magnifier(1280))).pack()
    tk.Button(root, text="XL (1600)",
              command=lambda: (root.quit(), root.destroy(), run_magnifier(1600))).pack()

    root.mainloop()

# --- PROD launch (headless, GPIO-ready) ---
def launch_prod():
    screen_width = 1280  # default width for production
    logger.info("Launching in PROD mode (GPIO controls expected)")
    setup_gpio_controls()
    run_magnifier(screen_width)

# --- Entry point ---
if __name__ == "__main__":
    if ENV_MODE.upper() == "DEV":
        launch_dev()
    else:
        launch_prod()

