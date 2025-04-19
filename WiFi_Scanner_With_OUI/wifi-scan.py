# Name: wifi-scan.py
#
# Micropython WiFi AP scanning program with
# OUI support!
#
# Blame: helmut.doring@slug.org
#

import sys
import network

red_ball = "🔴"
green_ball = "🟢"


class WifiManager:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self._scan_start = _thread.allocate_lock()
        self._scan_start.acquire()
        self._scan_complete = asyncio.ThreadSafeFlag()
        self._scan_thread = _thread.start_new_thread(self._scan, ())
        self._scan_results = None

    def _scan(self):
        while True:
            self._scan_start.acquire()
            try:
                self._scan_results = self.wlan.scan()
            except Exception as exc:
                sys.print_exception(exc)
                self._scan_results = []
            self._scan_complete.set()

    async def scan(self):
        self._scan_start.release()
        await self._scan_complete.wait()
        self._scan_complete.clear()
        return self._scan_results


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
    "WPA2/WPA3",
    "WPA3",
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
