import argparse
import time

from trinkeyfunctions import MyDevice

parser = argparse.ArgumentParser()
parser.add_argument("--port", "-p", default="/dev/ttyUSB0")
args = parser.parse_args()

print("starting setup")
device = MyDevice(args.port, startup="")  # perform no convenience imports

print("starting loop")
while True:
    device.try_touch()
    device.color_tic()
