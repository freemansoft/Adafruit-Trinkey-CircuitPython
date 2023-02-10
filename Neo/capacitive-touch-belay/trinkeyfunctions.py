from belay import Device


class MyDevice(Device):
    # NOTE: ``Device`` is captialized here!
    @Device.setup(
        autoinit=True
    )  # ``autoinit=True`` means method will be called during object creation.
    def setup():
        import time
        import board
        import touchio
        import usb_hid
        from adafruit_hid.keyboard import Keyboard
        from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
        from adafruit_hid.keycode import Keycode
        import neopixel

        # ===> These variables are not mutated by the functions
        keyboard = Keyboard(usb_hid.devices)
        keyboard_layout = KeyboardLayoutUS(keyboard)

        touch1 = touchio.TouchIn(board.TOUCH1)
        touch2 = touchio.TouchIn(board.TOUCH2)

        pixels = neopixel.NeoPixel(board.NEOPIXEL, 4)

        default_color = (1, 1, 1)  # color when button not pressed
        # this value is 600 when running all on the device
        cycle_length_tics = 99  # loop cycle time --> blink cycle length
        cycle_blank_length_tics = cycle_length_tics // 3  # blanking time

        # ===> These variables are shared and need to be global in the functions
        current_color = default_color  # button color or default_color
        current_tics = 0

    @Device.task
    def try_touch():
        # mark any updatable shared state variables as global
        global current_color
        global current_tics

        if touch1.value:  # If touch pad 1 is touched...
            current_color = (2, 0, 0)  # show touch detected
            pixels.fill(current_color)  # keep showing until not touching
            while touch1.value:  # Wait for release...
                time.sleep(0.1)
            keyboard.send(Keycode.WINDOWS, Keycode.L)  # Then send key press.
            current_color = (20, 0, 0)  # flash pattern will run with this color
            current_tics = 0  # reset tic counter so get a full cycle in this color
            print("Touch 1 Event")
        if touch2.value:  # If touch pad 2 is touched...
            current_color = (2, 2, 0)  # show touch detected
            pixels.fill(current_color)  # keep showing until not touching
            while touch2.value:  # Wait for release...
                time.sleep(0.1)
            keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.DELETE)
            current_color = (20, 20, 0)  # flash pattern will run with this color
            current_tics = 0  # reset tic counter so get a full cycle in this color
            print("Touch 2 Event")
            # Other HID keyboard possible actions
            # keyboard_layout.write("Hello World!\n")  # Then send string.

    @Device.task
    def color_tic():
        # mark any updatable shared state variables as global
        global current_color
        global current_tics
        # This is totally Brute Force and Ignorance (BFI)
        # blanks and resets color in last cycle_blank_length_tics through the cycle
        # three different led configurations - each 1/3 of non blank cycle
        # increments but rolls over the current tics if at end of cycle
        current_tics = (current_tics + 1) % cycle_length_tics
        # blank at end of the cycle so we always show color on change
        # alternate between two patterns because "why not"
        if current_tics == 1:
            pixels.fill((0, 0, 0))
            pixels[0] = current_color
            pixels[2] = current_color
            pixels.show()
        elif current_tics == (cycle_length_tics - cycle_blank_length_tics) // 3:
            pixels[1] = current_color
            pixels[3] = current_color
            pixels.show()
        elif current_tics == (cycle_length_tics - cycle_blank_length_tics) * 2 // 3:
            pixels[0] = (0, 0, 0)
            pixels[2] = (0, 0, 0)
            pixels.show()
        elif current_tics > cycle_length_tics - cycle_blank_length_tics:
            # turn off all the LEDs (blank)
            # reset to default for after blanking window
            # continually show blank until after blanking_window then restore color
            current_color = (0, 0, 0)
            pixels.fill(current_color)
            current_color = default_color
        # don't need this in belay because we're a LOT slower coming form the host
        # time.sleep(0.002)  # increases latency - alternative is to increase tics
