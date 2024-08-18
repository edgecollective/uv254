import board
import time
import busio as io
i2c = io.I2C(board.SCL, board.SDA)
import adafruit_ssd1306
#oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
#oled = adafruit_ssd1306.SSD1306_I2C(128,64,i2c,addr=0x3c)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
oled.fill(0)
oled.text('Hello', 0, 0, 1)
oled.text('World', 0, 10, 1)
oled.show()
