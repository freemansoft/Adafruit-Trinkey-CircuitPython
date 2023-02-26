"""
CircuitPython
Requires the following added to lib.
Some boards already have neopixel installed in their image
    adafruit_logging.py
    neopixel
Adjust the logging level in the call to main() at the bottom
    logging.DEBUG vs logging.INFO
Configure the Neopixel pin object and pixel count in call to main() at bottom

Tested on Adafruit Trinkey Neo

Reads messages over serial in this format
#<led><red><green><blue>-<time in msec>\n

<led> ff means all leds
<time in msec> period defaults to 1000 msec if no time provided

New commands completely replace the previous patterns
Uses a new line as a command terminator unlike some lights that stream


Valid test data
#ff000000
#ff010222
Clear the colors and then update one at a time
#ff000000-10#00050505-100#01100000-100#02001000-100#03000010-100
Bad Data that is accepted
#00A1A2A300-8888#00E1E2E3-0010
Bad Data
#000000
"""
import time
import board
import neopixel


class USBSerialReader:
    """
    Read a line from USB Serial (up to end_char), non-blocking, with optional echo
    https://github.com/todbot/circuitpython-tricks#read-user-input-from-usb-serial-non-blocking-mostly
    """

    import adafruit_logging as logging

    def __init__(self, logger):
        # the read buffer we append to
        self.s = ""
        self.logger = logger

    def read(self, end_char="\n", echo=True):
        import sys, supervisor

        n = supervisor.runtime.serial_bytes_available
        if n > 0:  # we got bytes!
            s = sys.stdin.read(n)  # actually read it in
            if echo:
                sys.stdout.write(s)  # echo back to human
            self.s = self.s + s  # keep building the string up
            if s.endswith(end_char):  # got our end_char!
                rstr = self.s  # save for return
                self.s = ""  # reset str to beginning
                return rstr
        return None  # no end_char yet


class ColorStep:
    """
    led is the led number - currently ignored
    rgb is a tuple of rgb values (r,g,b)
    hold_time is the time in msec to hold the color - currently ignored
    """

    import adafruit_logging as logging

    def __init__(self, led, rgb, hold_time):
        self.led = led
        self.rgb = rgb
        if hold_time == 0:
            self.hold_time = 1000
        else:
            self.hold_time = hold_time
        self.current_timer = 0

    def __str__(self):
        """Printing an individual ColorStep invokes this"""
        return f"({self.led},{self.rgb},{self.hold_time},{self.current_timer})"

    def __repr__(self):
        """Printing a list of ColorStep invokes this"""
        return f"({self.led},{self.rgb},{self.hold_time},{self.current_timer})"


class CommandProcessor:
    """
    Command Parser - such as it is converts commands into ColorSteps
    """

    import adafruit_logging as logging

    def __init__(self, logger):
        self.s = ""
        self.logger = logger

    def colorDuration(self, command_string):
        """
        returns time in msec or 0 if no time specified
        """
        parts = command_string.split("-")
        if len(parts) == 2:
            try:
                return int(parts[1])
            except ValueError:
                self.logger.error(f"Invalid time: {parts[1]} using:0")
                return 0
        else:
            return 0

    def colorSpecified(self, color_segment):
        """returns None if invalid color"""
        try:
            red = int(color_segment[2:4], 16)
            green = int(color_segment[4:6], 16)
            blue = int(color_segment[6:8], 16)
            return (red, green, blue)
        except ValueError as e:
            # self.logger.error(e)
            self.logger.error(f"invalid color: {color_segment}")
            raise e

    def processCommand(self, command_string):
        """
        returns a tuple (led_number, (r,g,b), hold_time)
        returns None if nothing could be processed
        """
        self.logger.debug(f"processing: {command_string}")
        command_segements = command_string.split("-")
        try:
            color_segment = command_segements[0]
            led = int(color_segment[0:2], 16)
            color = self.colorSpecified(color_segment)
            time = self.colorDuration(command_string)
            self.logger.debug(f"Received: ({led},{color},{time})")
            return ColorStep(led, color, time)
        except ValueError as e:
            # self.logger.error(e)
            self.logger.error(f"invalid command: {command_string}")
            return None


class PixelControl:
    """
    Neopixel control is managed in this class
    Understands fill and individual sets based on ColorSteps
    """

    import adafruit_logging as logging

    def __init__(self, pixels, logger):
        self.s = ""
        self.pixels = pixels
        self.logger = logger

    def updateColor(self, a_color_step):

        self.logger.debug(
            f"Updating: ({a_color_step.led},{a_color_step.rgb},{a_color_step.hold_time})"
        )
        if a_color_step.led == 255:
            # ignore the led for now
            self.pixels.fill(a_color_step.rgb)
        else:
            working_led = a_color_step.led
            working_led_index = 0
            while working_led != 0:
                if working_led & 1 == 1:
                    self.pixels[working_led_index] = a_color_step.rgb
                working_led = working_led >> 1
                working_led_index += 1
            self.pixels.write()


def main(neopixel_pin, neopixel_count, default_step, logger):
    import adafruit_logging as logging

    usb_reader = USBSerialReader(logger)
    color_command = CommandProcessor(logger)
    # This is hard coded to 8 neopixels cause why not
    # It shold work with any board that has 8 neopixels or less
    # Tested with the Adafruit Trinkey Neo
    pixels = neopixel.NeoPixel(neopixel_pin, neopixel_count)
    pixel_control = PixelControl(pixels, logger)

    active_patterns = [default_step]
    active_pattern_index = 0

    # TODO: Fix this complete and utter hack
    step_interval_sec = 0.01  # timer delay
    step_interval_msec = 50  # hack delay including serial polling time

    logger.info("type something and press and hit enter (newline)")
    while True:
        # https://github.com/todbot/circuitpython-tricks#read-user-input-from-usb-serial-non-blocking-mostly
        # read until newline, echo back chars - non blocking
        mystr = usb_reader.read()
        # mystr = usb_reader.read(end_char='\t', echo=False) # trigger on tab, no echo
        if mystr:
            mystr = mystr[: len(mystr) - 1]  # strip the end of line

            # A new line completely replaces the previous pattern
            if mystr.startswith("#"):
                active_patterns = []
                active_pattern_index = 0
                patterns = mystr.split("#")
                logger.debug(f"patterns: {patterns}")
                for pattern in patterns:
                    if len(pattern) > 0:  # optimization
                        a_color_step = color_command.processCommand(pattern)
                        # retain the requested number of steps even if an invalid step provided
                        # invalid are replaced with the default
                        if a_color_step:
                            active_patterns.append(a_color_step)
                        else:
                            active_patterns.append(default_step)
                        logger.debug(f"active_patterns: {active_patterns}")
                    else:
                        pass  # ignore empty
                pixel_control.updateColor(active_patterns[active_pattern_index])
            elif mystr == "?":
                print("Usage: [? | # | b]")
                print("?: this help")
                print("B: blank pixels")
                print("G: get current color and status")
                print("#nnrrggbb-msec#nnrrggbb-msec")
                print("#ff400000-1000#ff000040-1000")
            elif mystr == "B":
                # blank
                active_patterns = [default_step]
                active_pattern_index = 0
                pixel_control.updateColor(active_patterns[0])
            elif mystr == "G":
                print(active_patterns[active_pattern_index])
            else:
                logger.error(f"Unrecognized command: '{mystr}'")
        time.sleep(step_interval_sec)  # do something time critical
        if len(active_patterns) > 0:
            pattern = active_patterns[active_pattern_index]
            pattern.current_timer = pattern.current_timer + int(step_interval_msec)
            if pattern.current_timer > pattern.hold_time:
                pattern.current_timer = 0
                new_active_pattern_index = (active_pattern_index + 1) % len(
                    active_patterns
                )
                if new_active_pattern_index != active_pattern_index:
                    active_pattern_index = new_active_pattern_index
                    # logger.debug(f"Moving to pattern {active_pattern_index}")
                    pixel_control.updateColor(active_patterns[active_pattern_index])
        else:
            pass  # no active patterns


import adafruit_logging as logging

# Set this to logging.DEBUG if you want to see what is happening
target_neopixels = board.NEOPIXEL
num_neopixels = 8  # max we support anyway
default_step = ColorStep(0xFF, (0, 0, 0), 1000)
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

main(target_neopixels, num_neopixels, default_step, logger)
