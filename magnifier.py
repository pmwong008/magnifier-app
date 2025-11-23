import tkinter as tk
import cv2

def run_magnifier(screen_width):
    # Open camera
    cap = cv2.VideoCapture(0)

    # Set capture width (height can be auto or fixed)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
    
    zoom_factor = 1.0
    running = True
    
    while running:
        ret, frame = cap.read()
        if not ret:
            break
        
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
            break
        elif key == ord('+'): # zoom in
            print("Key pressed:", key)
            screen_width += 50
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
        elif key == ord('-'): # zoom out
            print("Key pressed:", key)
            screen_width = max(100, screen_width - 50)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)

    cap.release()
    cv2.destroyAllWindows()

def launch():
    try:
        width = int(entry.get())
    except ValueError:
        width = 640  # default
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
