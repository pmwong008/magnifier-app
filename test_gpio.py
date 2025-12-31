from gpiozero import Button
import signal

# Define buttons
btn_zoom_in  = Button(17, pull_up=True, bounce_time=0.05)
btn_zoom_out = Button(27, pull_up=True, bounce_time=0.05)
btn_quit     = Button(22, pull_up=True, bounce_time=0.05)
btn_wake     = Button(23, pull_up=True, bounce_time=0.05)

# Callbacks
def zoom_in():
    print("Zoom In button pressed")

def zoom_out():
    print("Zoom Out button pressed")

def quit_app():
    print("Quit button pressed")

def wake():
    print("Wake button pressed")

# Assign callbacks (note: no parentheses!)
btn_zoom_in.when_pressed  = zoom_in
btn_zoom_out.when_pressed = zoom_out
btn_quit.when_pressed     = quit_app
btn_wake.when_pressed     = wake

print("GPIO test running. Press buttons to see immediate responses.")
print("Press Ctrl+C to exit.")

# Keep the script alive
signal.pause()
