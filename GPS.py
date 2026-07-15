import sys, math, asyncio, sh1106, gc
from time import sleep
from machine import UART, SoftI2C, Pin, freq
from micropyGPS import MicropyGPS
from collections import deque

TZ_OFFSET = -7
# TZ_OFFSET = -8
LOG_FILE = "GPS_Log.txt"
logfile = open(LOG_FILE, "a")

ISO_DATETIME_FMT = "20{:02d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}{:6s}"

# Declock to 80MHz
freq(80000000)

# 1. Initialize UART
gps_serial = UART(2, baudrate=9600, tx=Pin(11), rx=Pin(12))

# 2. Instantiate the micropyGPS parser
my_gps = MicropyGPS(TZ_OFFSET)


## Statistical functions to be used on iterables,
## In this script mostly queues.
def mean(data):
    if len(data) == 0:
        return 0
    else:
        return sum(data) / len(data)


def variance(data):
    if len(data) < 3:
        return 0
    else:
        # Calculates sample variance (n-1)
        avg = mean(data)
        return sum((x - avg) ** 2 for x in data) / (len(data) - 1)


def stdev(data):
    return math.sqrt(variance(data))


## OLED Display
# from machine import SoftI2C, Pin
# import sh1106

# scl_pin = Pin(10, Pin.IN, Pin.PULL_UP)
# sda_pin = Pin(9, Pin.IN, Pin.PULL_UP)
scl_pin = 10
sda_pin = 9
reset_pin = None
lines = deque((), 5)
i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
print("Devices found via Software I2C:", [hex(d) for d in i2c.scan()])
display = sh1106.SH1106_I2C(128, 64, i2c, None, 0x3C)
display.sleep(False)


async def oled_display():
    i = 0
    display.fill(0)
    for line in lines:
        display.text(line, 0, i, 1)
        i += 12
    display.show()
    gc.collect()


## Construct an ISO Time string
def ISO_time():
    # Format: YYYY-MM-DDTHH:MM:SSZ
    iso_date_str = ISO_DATETIME_FMT.format(
        my_gps.date[2],  # Year (e.g., 26 for 2026)
        my_gps.date[1],  # Month
        my_gps.date[0],  # Day
        my_gps.timestamp[0],  # Hour
        my_gps.timestamp[1],  # Minute
        int(my_gps.timestamp[2]),  # Second
        f"-0{TZ_OFFSET}:00",
    )
    return iso_date_str


def print_location():
    print(" Latitude (DD): {:>9.6f}".format(mean(lat)))
    print("Longitude (DD): {:>9.6f}".format(mean(lon)))
    print("      Altitude: {:>7.2f} meters".format(mean(alt)))
    print("         Speed: {:>7.4f} km/h".format(mean(kph)))
    print("    Satellites: {}".format(int(mean(sat))))
    print("-" * 32)


# Rolling Average Globals
# from collections import deque
# from statistics  import mean
lat = deque((), 5)
lon = deque((), 5)
alt = deque((), 5)
kph = deque((), 5)
sat = deque((), 5)


def rolling_averages():
    # Format Location to standard Decimal Degrees (DD)
    # my_gps.latitude / longitude return a list: [degrees, minutes, 'N/S/E/W']
    lat_dd = my_gps.latitude[0] + (my_gps.latitude[1] / 60)
    if my_gps.latitude[2] == "S":
        lat_dd = -lat_dd

    lon_dd = my_gps.longitude[0] + (my_gps.longitude[1] / 60)
    if my_gps.longitude[2] == "W":
        lon_dd = -lon_dd

    ## We append to the queues and they keep the most recent 5 values
    lat.append(lat_dd)
    lon.append(lon_dd)
    alt.append(my_gps.altitude)
    kph.append(my_gps.speed[2])
    sat.append(my_gps.satellites_in_use)
    # caller should dereference mean(lat) etc.


## Are we moving?
def in_motion():
    vlat = variance(lat)
    vlon = variance(lon)

    # 1e-8 is probably a good value for production
    # 1e-10 is good for testing indoors
    if (abs(vlat) + abs(vlon)) > 1e-10:
        return True
    else:
        return False


def main():
    while True:
        if gps_serial.any():
            # Read raw stream from the module
            data = gps_serial.read()

            try:
                # Feed the micropyGPS parser
                for byte in data:
                    stat = my_gps.update(chr(byte))
            except IndexError:
                print(f"IndexError: byte:{byte} data len: {len(data)}")

            # If all is well
            if my_gps.valid:
                rolling_averages()
                if in_motion():
                    motion_data = f"{ISO_time()} {mean(lat):9.6f}, {mean(lon):9.6f} {mean(kph):7.4f} Kph"
                    logfile.write(f"{motion_data}\n")
                    lines.append(motion_data)
                    print(
                        f"https://www.google.com/maps/search/?api=1&query={mean(lat)}%2C{mean(lon)}"
                    )
                    print(f"ISO Time: {ISO_time()}")
                    print_location()
                    asyncio.run(oled_display())

        asyncio.sleep(0.2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down NOW...")
        logfile.close()
        del my_gps
        # i2c.deinit() does not exist here, so we do this:
        i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        display.sleep(True)
        sys.exit()
