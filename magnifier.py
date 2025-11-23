import tkinter as tk
import cv2

zoom_factor = 1.0

def run_magnifier(screen_width):
    # Open camera
    cap = cv2.VideoCapture(0)

    # Set capture width (height can be auto or fixed)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
    
    global zoom_factor
    running = True
    
    while running:
        ret, frame = cap.read()
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

    cap.release()
    cv2.destroyAllWindows()

def launch():
    try:
        width = int(entry.get())
    except ValueError:
        width = 800  # default
    root.destroy()
    run_magnifier(width)

# --- Landing Page ---
root = tk.Tk()
root.title("Magnifier Setup")

tk.Label(root, text="Enter screen width:").pack(pady=10)
entry = tk.Entry(root)
entry.pack(pady=5)

tk.Button(root, text="Start Magnifier", command=launch).pack(pady=20)

root.mainloop()
