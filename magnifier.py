import tkinter as tk
import cv2
import os
import time
import logging
from logging.handlers import RotatingFileHandler

# import gpiozero
# from gpiozero.pins.rpigpio import RPiGPIOPinFactory
# gpiozero.Device.pin_factory = RPiGPIOPinFactory()

from gpiozero import Button
import subprocess

def is_service_active(name="magnifier.service"):
    result = subprocess.run(["systemctl", "is-active", name], capture_output=True, text=True)
    return result.stdout.strip() == "active"

def toggle_magnifier():
    if is_service_active():
        subprocess.run(["systemctl", "stop", "magnifier.service"])
        print("Magnifier stopped")
    else:
        subprocess.run(["systemctl", "start", "magnifier.service"])
        print("Magnifier started")

def setup_service_toggle():
    btn_toggle = Button(22, pull_up=True, bounce_time=0.02)
    btn_toggle.when_pressed = toggle_magnifier
    logger.info("GPIO toggle ready. Press button to start/stop magnifier.")


# --- Environment flag ---
ENV_MODE = os.getenv("APP_MODE", "DEV")  # default to DEV if not set

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
logger.setLevel(logging.INFO) # default level

logger.handlers.clear() # clear existing (avoid duplicates if re-run)

# Formatter for all handlers
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", 
    datefmt="%H:%M:%S"   
)

if ENV_MODE.upper() == "DEV": 
    # Rotating file handler 
    file_handler = RotatingFileHandler("magnifier.log", maxBytes=500000, backupCount=3) 
    file_handler.setFormatter(formatter) 
    file_handler.setLevel(logging.INFO) 
    logger.addHandler(file_handler) 
    # Console handler 
    console_handler = logging.StreamHandler() 
    console_handler.setFormatter(formatter) 
    console_handler.setLevel(logging.INFO) 
    logger.addHandler(console_handler) 
    logger.info(f"Magnifier launched in {ENV_MODE.upper()} mode")

    
else: # PROD mode 
    # Console only, errors only 
    console_handler = logging.StreamHandler() 
    console_handler.setFormatter(formatter) 
    console_handler.setLevel(logging.ERROR) 
    logger.addHandler(console_handler)
    logger.info(f"Magnifier launched in {ENV_MODE.upper()} mode")

# Global state 
running = False 
zoom_factor = 1.0 

# Globals for GPIO buttons
btn_zoom_in = None
btn_zoom_out = None
btn_quit = None

# --- Control functions ---
def adjust_zoom(delta, source="GPIO"):
    global zoom_factor
    zoom_factor = max(1.0, zoom_factor + delta)
    print(f"Zoom adjusted: {zoom_factor:.1f}x ({source})")
    logger.info("Zoom adjusted: %.1fx (%s)", zoom_factor, source)

def stop_magnifier(source="GPIO"): 
    global running 
    if not running:
        return
    running = False
    cleanup_gpio()
    print(f"Quit requested ({source})") 
    logger.info("Quit requested (%s)", source) 
    # uncommnet the line below to stop the systemd service entirely.
    # subprocess.run(["systemctl", "stop", "magnifier.service"])

# --- GPIO setup (PROD only) ---
def setup_gpio_controls():
    global btn_zoom_in, btn_zoom_out, btn_quit
    
    btn_zoom_in  = Button(17, pull_up=True, bounce_time=0.05)
    btn_zoom_out = Button(27, pull_up=True, bounce_time=0.05)
    btn_quit     = Button(22, pull_up=True, bounce_time=0.05)

    btn_zoom_in.when_pressed  = lambda: adjust_zoom(+0.1, source="GPIO")
    btn_zoom_out.when_pressed = lambda: adjust_zoom(-0.1, source="GPIO")
    btn_quit.when_pressed     = lambda: stop_magnifier(source="GPIO")

    logger.info("GPIO buttons initialized and callbacks registered")

def cleanup_gpio():
    btn_zoom_in.close()
    btn_zoom_out.close()
    btn_quit.close()
    logger.info("GPIO buttons cleaned up!")
    
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

# Run Magnifier Loop
def run_magnifier(screen_width=1280):
    camera_type, cam = get_camera_source()
    global zoom_factor, running
    # current_frame, current_width, current_height
    running = True
    
    logger.info("Magnifier started with width %d", screen_width)
    
    while running:
        if camera_type == "pi":
            frame = cam.capture_array()
        else:
            ret, frame = cam.read()
            if not ret or frame is None:
                logger.warning("No frame captured, skipping iteration")
                # logger.error("Failed to capture frame from PiCamera/webcam")
                time.sleep(0.05) #short pause before retry
                # break
                continue

        # --- Apply zoom by cropping ---
        h, w = frame.shape[:2]
        if h == 0 or w == 0:
            logger.warning("Invalid frame dimensions, skipping iteration")
            continue
        
        if zoom_factor > 1.0:
            new_w = int(w / zoom_factor)
            new_h = int(h / zoom_factor)
            if new_w <= 0 or new_h <=0:
                logger.warning("Zoom factor too high, skipping iteration")
                continue
            x1 = (w - new_w) // 2
            y1 = (h - new_h) // 2
            frame = frame[y1:y1+new_h, x1:x1+new_w]

        # --- Resize to chosen screen width ---
        if frame.shape[1] == 0:
            logger.warning("Frame width is zero, skipping iteration")
            continue
        height = int(frame.shape[0] * (screen_width / frame.shape[1]))
        if height <=0:
            logger.warning("Calculated height invalid, skipping iteration")
            continue
        
        frame = cv2.resize(frame, (screen_width, height))

        # --- Update globals for wake_screen (AFTER resize) ---
        # current_frame = frame
        # current_width = screen_width
        # current_height = height

        # --- Show the frame ---
        cv2.imshow("Magnifier", frame)
        cv2.resizeWindow("Magnifier", screen_width, height)

        # --- Keyboard controls ---
        key = cv2.waitKey(1) & 0xFF
        # if key == ord('q'): quit_app(source="Keyboard")
        if key in (ord('+'), ord('i')):
            adjust_zoom(+0.1, source="Keyboard")
        elif key in (ord('-'), ord('o')):
            adjust_zoom(-0.1, source="Keyboard")
        # elif key == ord('w'): wake_screen(source="Keyboard")

        time.sleep(0.01)
        
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
    logger.info("GPIO controls registered: zoom in/out, quit")
    run_magnifier(screen_width)

# --- Entry point ---

if __name__ == "__main__":
    
    logger.info("APP_MODE=%s", ENV_MODE)
    if ENV_MODE.upper() == "PROD":
        setup_service_toggle()
        launch_prod()   # GPIO buttons, ON/OFF appliance mode
    else:
        launch_dev()    # keyboard shortcuts


