# SPDX-FileCopyrightText: 2022 Joe Freeman joe@freemansoft.com
#
# SPDX-License-Identifier: MIT
#

import argparse
import time

from trinkeyfunctions import MyDevice

parser = argparse.ArgumentParser()
parser.add_argument("--port", "-p", default="/dev/ttyUSB0")
args = parser.parse_args()

device = MyDevice(args.port, startup="")  # perform no convenience imports

while True:
    device.try_touch()
    device.color_tic()
