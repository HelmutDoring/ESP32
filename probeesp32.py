# Name: probeesp32.py
#
# Report memory and disk usage of an esp32 board
#
# Blame: helmut.doring@slug.org
#


import esp
import io
import uos as os
import gc
import sys
import machine

# For the sake of consistency, the MAC address is
# the unique i.d. in MicroPython. Note that the
# IEEE defines the OUI assignments, and there
# are 224 assigned to Espressif!
mac_addr = machine.unique_id()
mac_addr = "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*mac_addr)
print(f"Unique ID: {mac_addr}")

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


def free(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    F = int(F / 1024)
    T = int(T / 1024)
    P = int(T - F)
    print(f"RAM: {P} kB used of {T} ({F} free)")


df()
free()
print("\n")
tree("")
