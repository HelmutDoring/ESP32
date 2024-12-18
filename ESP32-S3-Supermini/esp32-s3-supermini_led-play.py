#
# This is an RGB LED exerciser for the
# ESP32 S3 Supermini Development Board as
# Found on AliExpess.
#
# The relative weights of the colors are
# what seem to me to look pleasing.
#
# Blame: helmut.doring@slug.org
#

from machine import Pin
from time import sleep
from neopixel import NeoPixel
from random import randrange

pin = Pin(48, Pin.OUT)  # Pin for RGB led on ESP32-S3 Supermini
led = NeoPixel(pin, 1)  # "1" = one RGB led on the "led bus"

while True:
    red = randrange(1, 14, 2)
    green = randrange(1, 10, 2)
    blue = randrange(1, 6, 2)
    led[0] = (red, green, blue)
    led.write()
    sleep(0.1)
