# Name: probeesp32.py
#
# Report memory and disk usage of an esp32 board
#
# Now uses ouitext OUI database from wifi-scanner.py
#
# Blame: helmut.doring@slug.org
#

import esp
import esp32
import io
import uos as os
import gc
import sys
import machine

def oui_text_search(hex):
    oui_db = f"./ouitext/{hex[0:1]}.txt"
    print(f"{oui_db}")
    with open(oui_db, "r") as file:
        for line in file:
            if line[:8] == hex:
                file.close()
                return line.strip()

# For the sake of consistency, the MAC address is
# the unique i.d. in MicroPython. Note that the
# IEEE defines the OUI assignments, and there
# are 224 assigned to Espressif!
mac_addr = machine.unique_id()
mac_addr = "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*mac_addr)
print(f"Unique ID: {mac_addr}")
mfg = oui_text_search(mac_addr[:8].upper())
print(f"OUI Manufacturer: {mfg}")
print(f"pyboard: {sys.platform}")


def tree(root):
    try:
        for dirent in os.listdir(root):
            fstat = os.stat(f"{root}/{dirent}")
            fsize = fstat[6]
            if fsize > 1024:
                fsize = int(fsize / 1024)
                unit = "kB"
            else:
                unit = "B"
            print(f"{root}/{dirent} {fsize} {unit}")
            tree(root + "/" + dirent)
    except OSError as e:
        pass


def df():
    s = esp.flash_size()
    print(f"Flash size: {int(s / 1024)} kB")
    # os.statvfs reports BLOCKS, not bytes
    s = os.statvfs("/")
    total = int(s[0] * s[2] / 1024)
    free = s[0] * int(s[3] / 1024)
    used = total - free
    print(f"Disk: {used} kB used of {total} ({free} free)")


def free():
    gc.collect()
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    free = int(free / 1024)
    total = int(total / 1024)
    used = int(total - free)
    print(f"RAM: {used} kB used of {total} ({free} free)")


def cpuinfo():
    cpu_freq = machine.freq()
    sys_info = os.uname()
    cpu_type = sys_info.machine

    if "ESP32S3" in cpu_type:
        mcu_type = "Xtensa LX7 Dual-core"
    elif "ESP32C3" in cpu_type:
        mcu_type = "RISC-V Single-core"
    elif "ESP32" in cpu_type:
        mcu_type = "Xtensa LX6 Dual-core"
    else:
        mcu_type = cpu_type
        
    print(f"CPU Frequency: {cpu_freq / 1_000_000} MHz")
    print(f"Chip/Platform: {mcu_type}")
    print(f"Firmware Build: {sys_info.version}")
    try:
        raw = esp32.raw_temperature()
        print(f"Internal Die Temp: {raw}°F {(raw - 32) * 5/9}°C")
    except Exception as e:
        raw = esp32.mcu_temperature()
        print(f"Internal Die Temp: {raw * 9/5 + 32}°F {raw}°C")

cpuinfo()
df()
free()
print("\n")
tree("")
