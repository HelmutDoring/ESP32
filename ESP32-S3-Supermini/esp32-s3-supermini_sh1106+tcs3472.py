import sys
sys.path.append("/hwlib")

from time import sleep
from machine import Pin, SoftI2C
import sh1106  # OLED display
from tcs3472 import tcs3472  # RGB Color Sensor


def getrgb():
    p0.on()  # Turn on LED's
    SCL = 12  # Or whatever public pin you choose
    SDA = 11  # Or whatever public pin you choose
    bus = SoftI2C(sda=Pin(SDA), scl=Pin(SCL))
    tcs = tcs3472(bus, 0x29)  # Default address for tcs3472
    color = tcs.rgb()
    p0.off()  # Turn off LED's
    return color


def write_oled(rgb):
    SCL = 9 # Or whatever... etc.
    SDA = 8 # Ditto.
    RST = 4 # This pin is commonly marked "EN"
    FREQ = 1000000
    bus = SoftI2C(scl=Pin(SCL), sda=Pin(SDA), freq=FREQ)
    oled = sh1106.SH1106_I2C(128, 64, bus, Pin(RST), 0x3C)
    oled.sleep(False)
    oled.fill(0)
    msg = ', '.join(map(str, rgb))
    oled.text(msg, 0, 32 , 1)
    oled.show()


p0 = Pin(10, Pin.OUT)  # cfg pin 10 to control illuminator LEDs
while True:
    write_oled(getrgb())
    sleep(1)
