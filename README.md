# Adafruit Trinkey Sandbox

Explorations on the [Adafruit Neo Trinkey - SAMD21 USB Key with 4 NeoPixels](https://www.adafruit.com/product/4870) using CircuitPython as Adafruit intended!

## projects
1. `capacitive-touch` the copacitive touch demo with better LED control
1. `capacitive-touch-belay` the capacative touch demo with better LED control managed by `belay`
1. `indicator-light` a command line based NeoPixel indicator light to be used as 1 or more status indicators.

## How does a Trinkey Neo Report on USB

The out of the box report on a Mac looks like this.  Notice the VID and PID because they are used by some software.
You can see this VID and PID on a windows machine when you examine the COM port expsed as one of the USB devices.

```
NeoPixel Trinkey M0:

   Product ID: 0x80f0
   Vendor ID: 0x239a
   Version: 1.00
   Serial Number: CA1747C34B48585020312E3521280EFF
   Speed: Up to 12 Mb/s
   Manufacturer: Adafruit Industries LLC
   Location ID: 0x02100000 / 1
   Current Available (mA): 500
   Current Required (mA): 100
   Extra Operating Current (mA): 0
   Media:
   NeoPixel Trinkey:
      Capacity: 66 KB (66,048 bytes)
      Removable Media: Yes
      BSD Name: disk4
      Logical Unit: 0
      Partition Map Type: MBR (Master Boot Record)
      S.M.A.R.T. status: Verified
      USB Interface: 2
      Volumes:
         CIRCUITPY:
         Capacity: 66 KB (65,536 bytes)
         Free: 32 KB (32,256 bytes)
         Writable: Yes
         File System: MS-DOS FAT12
         BSD Name: disk4s1
         Mount Point: /Volumes/CIRCUITPY
         Content: DOS_FAT_12
         Volume UUID: D9E0500C-524E-39A8-A778-C125384249C0
```
