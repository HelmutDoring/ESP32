import sys

sys.path.append("/hwlib")

from time import sleep
from machine import Pin, SoftI2C
import sh1106  # OLED display
from tcs3472 import tcs3472  # RGB Color Sensor


def getrgb():
    p0.on()  # Turn on LED's
    SCL = 5  # Or whatever public pin you choose
    SDA = 6  # Or whatever public pin you choose
    bus = SoftI2C(sda=Pin(SDA), scl=Pin(SCL))
    tcs = tcs3472(bus, 0x29)  # Default address for tcs3472
    color = tcs.rgb()
    sleep(0.2)
    p0.off()
    sleep(2)
    return color


def write_oled(rgb):
    SCL = 1
    SDA = 2
    RST = 4
    FREQ = 1000000
    bus = SoftI2C(scl=Pin(SCL), sda=Pin(SDA), freq=FREQ)
    oled = sh1106.SH1106_I2C(128, 64, bus, Pin(RST), 0x3C)
    oled.sleep(False)
    oled.fill(0)
    msg = ", ".join(map(str, rgb))
    oled.text(msg, 0, 28, 1)
    oled.show()


p0 = Pin(4, Pin.OUT)  # cfg pin to control illumination LEDs on RGB sensor
while True:
    write_oled(getrgb())



