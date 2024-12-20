# If your root directory is not named "/pyboard/" you installed the wrong MicroPython bin file.
./rshell/r.py --port /dev/ttyACM0 cp -r ./mipyshell/bin /pyboard/
./rshell/r.py --port /dev/ttyACM0 cp -r ./mipyshell/lib /pyboard/
