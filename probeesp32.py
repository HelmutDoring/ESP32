# Name: probeesp32.py
#
# Report memory and disk usage of an esp32 board
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
    oui_db = f"./lib/ouitext/{hex[0:1]}.txt"
    with open(oui_db, "r") as file:
        for line in file:
            if line[:8] == hex:
                file.close()
                return line.strip()


# IEEE defines the OUI assignments, and there
# are 224 assigned to Espressif!
mac_addr = machine.unique_id()
mac_addr = "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*mac_addr)
print(f"Unique ID: {mac_addr}")
mfg = oui_text_search(mac_addr[:8].upper())[11:]
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
            elif fsize == 0:
                fsize = ''
                unit = ''
            else:
                unit = "B"
            print(f"{root}/{dirent} {fsize} {unit}")
            tree(root + "/" + dirent)
    except OSError as e:
        pass


def df():
    s = esp.flash_size()
    print(f"Flash(kB): {int(s / 1024)}")
    # os.statvfs reports BLOCKS, not bytes
    s = os.statvfs("/")
    total = int(s[0] * s[2] / 1024)
    free = int(s[0] * s[3] / 1024)
    used = total - free
    print(f"DISK(kB) - Total: {total} Used: {used} Free: {free}")


def free():
    gc.collect()
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    free = int(free / 1024)
    total = int(total / 1024)
    used = int(total - free)
    print(f"RAM(kB) - Total: {total} Used: {used} Free: {free}")


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

    print(f"CPU Frequency: {int(cpu_freq / 1_000_000)} MHz")
    print(f"Chip/Platform: {mcu_type}")
    print(f"Firmware Build: {sys_info.version}")
    try:
        raw = esp32.raw_temperature()
        ctemp = int((raw - 32) * 5/9)
        print(f"Internal Die Temp: {raw}°F {ctemp}°C")
    except Exception:
        raw = esp32.mcu_temperature()
        ftemp = int(raw * 9/5 + 32)
        print(f"Internal Die Temp: {ftemp}°F {raw}°C")


cpuinfo()
df()
free()
print("\n")
tree("")
