import time
import board
import analogio
adc = analogio.AnalogIn(board.A1)

while True:
    voltage=adc.value / 65535 * adc.reference_voltage
    #voltage = adc.value / 65535 * 3.3
    #print(adc.reference_voltage)
    print(voltage)
    time.sleep(.1)
