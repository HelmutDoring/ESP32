# This will use all 8MB ram and 16MB filesystem!
./esptool/esptool.py --chip esp32-S3 --port /dev/ttyACM0 write_flash -z 0x0 ./MicroPython_binfiles/ESP32_GENERIC_S3-SPIRAM_OCT_8MB-20241129-v1.24.1.bin
mp-image-tool-esp32 a0 -f 16M --resize vfs=0
mp-image-tool-esp32 a0 --fs grow vfs
mp-image-tool-esp32 a0
