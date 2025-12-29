from gpiozero import Button
from signal import pause

btn_zoom_in  = Button(17, pull_up=True)
btn_zoom_out = Button(27, pull_up=True)
btn_quit     = Button(22, pull_up=True)
btn_wake     = Button(23, pull_up=True)

def zoom_in(): print("Zoom In pressed")
def zoom_out(): print("Zoom Out pressed")
def quit_app(): print("Quit pressed")
def wake_screen(): print("Wake pressed")

btn_zoom_in.when_pressed  = zoom_in
btn_zoom_out.when_pressed = zoom_out
btn_quit.when_pressed     = quit_app
btn_wake.when_pressed     = wake_screen

print("Ready. Press buttons...")
pause()  # keeps script running
