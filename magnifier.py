import tkinter as tk
import cv2

zoom_factor = 1.0

def get_camera_source():
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
        picam2.start()
        print("Using Pi Camera via Picamera2")
        return ("pi", picam2)
    except Exception:
        print("Pi Camera not available, falling back to USB webcam")
        cap = cv2.VideoCapture(0)
        return ("usb", cap)
    
def run_magnifier(screen_width):
    # Open camera
    # cap = cv2.VideoCapture(0)

    # Set capture width (height can be auto or fixed)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
    camera_type, cam = get_camera_source()
    global zoom_factor
    running = True
    
    while running:
        if camera_type == "pi":
            frame = cam.capture_array()
        else:
            ret, frame = cam.read()
            if not ret:
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

        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):   # quit
            print("Key pressed:", key)
            running = False
            # break
        elif key == ord('+'):
            zoom_factor += 0.1
            print(f"Zoom in: {zoom_factor:.1f}x")
        elif key == ord('-'):
            zoom_factor = max(1.0, zoom_factor - 0.1)
            print(f"Zoom out: {zoom_factor:.1f}x")

    if camera_type == "pi":
        cam.stop()
    else:
        cam.release()
    cv2.destroyAllWindows()

def launch_window():
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

# --- Entry point ---
if __name__ == "__main__":
    launch_window()
