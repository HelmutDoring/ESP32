# Name: wifi-scan.py
#
# Micropython WiFi AP scanning program with
# OUI support!
#
# Default is to use the "ouitext" directory
# of OUI database files generated by running
# the utility mac-addr-to-mfg.sh after
# downloading the OUI database from IEEE:
#
#  https://standards-oui.ieee.org/oui/oui.txt
#
# Blame: helmut.doring@slug.org
#

import sys
import network

red_ball = "🔴"
green_ball = "🟢"


def mac_fmt(bssid):
    return "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*bssid)


def oui_text_search(hex):
    oui_db = f"./ouitext/{hex[0:1]}.txt"
    with open(oui_db, "r") as file:
        for line in file:
            # line = line.strip()
            if line[:8] == hex:
                file.close()
                return line.strip()


def oui_db_search(hex):
    if "ouidict" not in sys.modules:
        from ouidict import ouidict
    return ouidict[hex]


authmodes = [
    "Open",
    "WEP",
    "WPA-PSK",
    "WPA2-PSK",
    "WPA/WPA2-PSK",
    "WPA2-ENTERPRISE",
    "UNKNOWN (MODE 6)",
    "WPA2/WPA3",
]

network.WLAN(network.STA_IF).active(False)
ap = network.WLAN(network.STA_IF)
ap.active(True)
network.WLAN(network.AP_IF).active(False)
# We're only listening, so don't need POWER.
ap.config(txpower=2, pm=network.WLAN.PM_NONE)

f = open("wifi-scan-output.txt", "a")
i = 0

for ssid, bssid, channel, RSSI, authmode, hidden in ap.scan():
    i += 1

    mac = mac_fmt(bssid)
    # uncomment the next line for text-based search.
    mfg = oui_text_search(mac[:8].upper())
    # uncomment the next line to use the Python dict.
    # mfg = oui_db_search(mac[:8].upper())
    mode = authmodes[authmode]
    hidden = "(hidden)" if hidden else ""

    if mode == "Open":
        ball = red_ball
    else:
        ball = green_ball

    result = (
        f"{i}: {ssid.decode()}\n"
        f"   - Auth: {ball} {mode} {hidden}\n"
        f"   - Channel: {channel}\n"
        f"   - RSSI: {RSSI}\n"
        f"   - BSSID: {mac}\n"
        f"   - MFG: {mfg}\n"
    )

    f.write(f"{result}\n")
    print(result)
    result = ""

f.close()
ap.active(False)
sys.exit()
