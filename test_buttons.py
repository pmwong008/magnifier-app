# import gpiozero
# from gpiozero.pins.rpigpio import RPiGPIOPinFactory
# gpiozero.Device.pin_factory = RPiGPIOPinFactory()

# from gpiozero import Button
# import signal

# from signal import pause
'''
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
'''

'''
btn1 = Button(17, pull_up=True)
btn2 = Button(27, pull_up=True)
btn3 = Button(22, pull_up=True)
btn4 = Button(23, pull_up=True)

btn1.when_pressed = lambda: print("Button 1 (GPIO17) pressed")
btn2.when_pressed = lambda: print("Button 2 (GPIO27) pressed")
btn3.when_pressed = lambda: print("Button 3 (GPIO22) pressed")
btn4.when_pressed = lambda: print("Button 4 (GPIO23) pressed")

print("Press each button...")
'''
from gpiozero import Button
import signal

btn = Button(17, pull_up=True)  # no bounce_time

def pressed():
    print("Button pressed instantly!")

btn.when_pressed = pressed

print("Waiting for button presses on GPIO17...")
signal.pause()


