## Capacitive touch run with Belay

# Prequisites
1. Trinkey Neo running CircuitPython

# Running
1. Run `python3 main_belay.py -p <com-port>` to start execution

# Usage
1. This will roll through a pattern in white on the neopixel waiting for your to touch one of the two touch censors.
1. When you touch one of the touch pads, the Neopixels will freeze in a dim color that is associated with the touch pad
1. When you stop touch the touch pads, the program will send a key combination over the HID connection and change the Neopixels to a bright version of the color assicated with at touch pad.
1. The Neopixels will cycle though the normal pattern with the touch censors color one time and then switch back to the white pattern.

# Flow

```mermaid
flowchart LR
    subgraph pc[On the PC]
        subgraph main_belay.py
            Startup --> initialize[Initialize MyDevice]
            initialize --4 start run loop--> While[While True]
            While --> device_trytouch[device.try_touch]
            device_trytouch --> device_colortic[device.color_tic]
            device_colortic --> device_trytouch
        end

        subgraph MyDevice[trinkeyfunctions.py MyDevice]
            def_setup[def setup]
            def_trytouch[def try_touch]
            def_trycolortic[def try_tic]
        end
    end

    subgraph trinkey[On the Trinkey device]
        subgraph trinkeyfunctionssetup[MyDevice Global]
            setup[def setup]
        end
        subgraph trinkeyfunctions[MyDevice Functions]
            try_touch[def try_touch]
            color_tic[def color_tic]
        end
    end

initialize --1:execute setup global scope--> def_setup
initialize --2:download and create executer--> def_trytouch
initialize --3:download and create executer--> def_trycolortic


device_trytouch --call--> try_touch
device_colortic --call--> color_tic

def_setup-.downloaded and execute global.->setup
def_trytouch-.downloaded to device.->try_touch
def_trycolortic -.downloaded to device.->color_tic
```