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

ave_count = 10.

while True:

    voltage_ave = 0
    for i in range(0,ave_count):
        voltage=adc.value / 65535 * adc.reference_voltage
        #voltage = 4.
        voltage_ave=voltage_ave+voltage
        time.sleep(.1)
    voltage_ave=voltage_ave/ave_count
    
    volts_str='{:03.3f}'.format(voltage_ave)
    
    print(volts_str)
    #time.sleep(1)
    
