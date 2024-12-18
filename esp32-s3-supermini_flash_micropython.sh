./esptool/esptool.py --chip esp32-S3 --port /dev/ttyACM0 erase_flash
./esptool/esptool.py --chip esp32-S3 --port /dev/ttyACM0 write_flash -z 0x0 ESP32_GENERIC_S3-FLASH_4M-20241129-v1.24.1.bin
