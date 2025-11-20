#!/usr/bin/env python3
import cv2

def main():
    # Open the default webcam (usually /dev/video0 on Raspberry Pi)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Window name
    window_name = "Magnifier App"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # --- Magnifier effect ---
        # Resize the frame to 2x for magnification
        magnified = cv2.resize(frame, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)

        # Show the magnified frame
        cv2.imshow(window_name, magnified)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
