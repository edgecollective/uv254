# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid white
background, a smaller black rectangle, and some white text.
"""

import board
import displayio
import digitalio
import analogio
import time
import math


adc = analogio.AnalogIn(board.A5)

while True:

    voltage=adc.value / 65535 * adc.reference_voltage
    volts_str='{:03.3f}'.format(voltage)
    
    print(volts_str)
    time.sleep(.1)
    
