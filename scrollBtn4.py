#!/usr/bin/env python3
import evdev
import uinput
from evdev import InputDevice, categorize, ecodes
import select
import evdev

#
# This script replace the BTN4 of my Adept trackball with a 2D scroll
##

# Change to your actual mouse device
# DEVICE_NAME = "Logitech MX Master"
DEVICE_NAME = "Ploopy Corporation Ploopy Adept Trackball Mouse"
QMK_KEYBOARD_KEYBOARD_NAME = "Diego Palacios cantor Mouse"

# Lower = less sensitive, try 0.02-0.4
SCROLL_SENSITIVITY = 0.05

# Constants for event codes
EV_KEY = 1
BTN_SIDE = 275
EV_REL = 2
REL_X = 0
REL_Y = 1

def print_devices():
    print('Available devices:')
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        print(f"\t{dev.name}")



# Find the device based on the names configured
def find_device_path(name):
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        if name in dev.name:
            return path
    raise RuntimeError(f"Device with name '{name}' not found.")

print_devices()

trackball_path = find_device_path(DEVICE_NAME)
qmk_keyboard_path = find_device_path(QMK_KEYBOARD_KEYBOARD_NAME)

trackball = InputDevice(trackball_path)
qmk_keyboard = InputDevice(qmk_keyboard_path)

print('----------------------------------')
print('Script started! Enjoy your scroll!')

ui = uinput.Device([
    uinput.REL_WHEEL,
    uinput.REL_HWHEEL,
    uinput.BTN_LEFT,
    uinput.BTN_RIGHT
])

scrolling = False
scroll_accum_x = 0.0
scroll_accum_y = 0.0

def handle_btn4(event):
    global scrolling
    if event.value == 1:
        scrolling = True
        trackball.grab()
        qmk_keyboard.grab()
    elif event.value == 0:
        scrolling = False
        trackball.ungrab()
        qmk_keyboard.ungrab()

try:
    while True:
        r, _, _ = select.select([trackball, qmk_keyboard], [], [])
        for dev in r:
            for event in dev.read():
                if dev == trackball:
                    if event.type == EV_KEY and event.code == BTN_SIDE:
                        handle_btn4(event)
                    elif scrolling and event.type == EV_REL:
                        if event.code == REL_X:
                            if abs(event.value) > 0:
                                scroll_accum_x += event.value * SCROLL_SENSITIVITY
                                emit_value = int(scroll_accum_x)
                                if emit_value != 0:
                                    ui.emit(uinput.REL_HWHEEL, emit_value)
                                    scroll_accum_x -= emit_value
                        elif event.code == REL_Y:
                            if abs(event.value) > 0:
                                scroll_accum_y -= event.value * SCROLL_SENSITIVITY  # Y is inverted
                                emit_value = int(scroll_accum_y)
                                if emit_value != 0:
                                    ui.emit(uinput.REL_WHEEL, emit_value)
                                    scroll_accum_y -= emit_value
                elif dev == qmk_keyboard:
                    if event.type == EV_KEY and event.code == BTN_SIDE:
                        handle_btn4(event)
except KeyboardInterrupt:
    trackball.ungrab()
    qmk_keyboard.ungrab()
