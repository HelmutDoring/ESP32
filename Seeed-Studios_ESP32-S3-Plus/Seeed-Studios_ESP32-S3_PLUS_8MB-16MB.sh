#!/bin/bash
# MicroPython install and setup script for the Seeed Studios XIAO ESP32-S3-Plus
# This will use all 8MB ram and 16MB filesystem!
#
# Blame: helmut.doring@slug.org

# This is the easiest way to go, avoiding some peculiarities of mp-image-tool-esp32
esptool.py --chip esp32-S3 --port /dev/ttyACM0 write_flash -z 0x0 ESP32_GENERIC_S3-SPIRAM_OCT-20250415-v1.25.0.bin

# Note: "a0" is mp-image-tool-esp32's way of referring to /dev/ttyACM0
# Likewise, "u0" refers to /dev/ttyUSB0, and so forth
mp-image-tool-esp32 a0 --flash-size 16M --resize vfs=0
mp-image-tool-esp32 a0 --fs grow vfs
mp-image-tool-esp32 a0
