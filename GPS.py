import sys, math
from time import sleep
from machine import UART, Pin
from micropyGPS import MicropyGPS

TZ_OFFSET = -7
#TZ_OFFSET = -8
LOG_FILE = 'GPS_Log.txt'
logfile = open(LOG_FILE, "a")

ISO_FMT = '20{:02d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}{:6s}'

# 1. Initialize UART
gps_serial = UART(2, baudrate=9600, tx=Pin(11), rx=Pin(12))

# 2. Instantiate the micropyGPS parser
my_gps = MicropyGPS(TZ_OFFSET)

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

def ISO_time():
    # Format: YYYY-MM-DDTHH:MM:SSZ
    iso_date_str = ISO_FMT.format(
        my_gps.date[2],           # Year (e.g., 26 for 2026)
        my_gps.date[1],           # Month
        my_gps.date[0],           # Day
        my_gps.timestamp[0],      # Hour
        my_gps.timestamp[1],      # Minute
        int(my_gps.timestamp[2]), # Second
        f"-0{TZ_OFFSET}:00"
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
from collections import deque
#from statistics  import mean
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
        
    lat.append(lat_dd)
    lon.append(lon_dd)
    alt.append(my_gps.altitude)
    kph.append(my_gps.speed[2])
    sat.append(my_gps.satellites_in_use)
    # caller should dereference mean(lat) etc.

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
                if mean(kph) >= 2:
                    #logfile.write(f"{ISO_time()} ")
                    print(f"ISO Time: {ISO_time()}")
                    print_location()
                    print(f"https://www.google.com/maps/search/?api=1&query={mean(lat)}%2C{mean(lon)}")
        
        sleep(0.2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down NOW...")
        logfile.close()
        del my_gps
        sys.exit()
