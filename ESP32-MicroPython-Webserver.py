# A basic Micropython webserver for the ESP32
#
# NOTE: We never close the reader socket because
# there is an implicit SO_REUSEADDR
#
# Blame: Helmut.Doring@slug.org
#

import re, sys, time, network, ubinascii, uasyncio, gc

DEBUG = True
counter = 0
port = 8080
ssid = "MY_ESSID"
password = "MY_PASSWORD"
myip = "192.168.1.111"
netmask = "255.255.255.0"
gateway = "192.168.1.254"
dnshost = gateway
return_code = "200 OK"

gc.collect()
gc.enable()


def increment():
    global counter
    counter += 1


def decrement():
    global counter
    counter -= 1


def free():
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = "{0:.2f}%".format(F / T * 100)
    return "Total:{0} Free:{1} ({2})".format(T, F, P)


async def connect_wifi():
    network.WLAN(network.STA_IF).active(False)
    network.WLAN(network.AP_IF).active(False)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    # txpower=8.5 is a "reliability hack" for low power radios.
    # Better is to add a ~500uF-1000uF Electrolytic capacitor
    # across the 3.3v and GND pins to handle current spikes up
    # to 500mA. But I am not 100% certain this does anything
    # at all!
    sta_if.config(txpower=8.5)
    # Disable WLAN power saving to speed things up a hair.
    # PM_POWERSAVE and PM_PERFORMANCE are other options.
    sta_if.config(pm=sta_if.PM_NONE)

    print("Connecting to network...")
    try:
        sta_if.connect(ssid, password)
    except Exception as e:
        print(f"Error: {e}")

    # pass a 4-tuple!
    sta_if.ifconfig((myip, netmask, gateway, dnshost))
    while not sta_if.isconnected():
        await uasyncio.sleep_ms(200)

    mac = ubinascii.hexlify(sta_if.config("mac"), ":").decode()
    print(f"MAC ADDRESS: {mac}")
    print("IP ADDRESS: ", sta_if.ifconfig()[0])


async def read_reader(reader):
    global return_code
    request = "/"
    path = "/"
    request_rx = "^GET\s+(.+)\s+HTTP"
    data = await reader.readline()
    try:
        request = data.decode("utf-8")
        if request is not None:
            path = re.match(request_rx, request).group(1)

    except Exception as e:
        return_code = "403 Forbidden"
        if "NoneType" in repr(e):
            err = f"{e} (possible open-proxy relay attempt)"
        else:
            err = f"{e} (please code a handler for this!)"

        print(f"Bad Request: {err}")
        print(f"Request: '{request.strip()[:80]}'")
    return path


async def craft_response(request):
    global return_code
    preamble = f"HTTP/1.1 {return_code}\r\nContent-Type:"
    content_type = "text/plain\r\n"
    content = f"{request}\r\n"  ## REPLACE THIS WITH YOUR HANDLER!
    content_length = f"Content-Length: {len(content)}\r\n"
    epilog = "Connection: close\r\n\r\n"
    response = f"{preamble}{content_type}{content_length}{epilog}{content}"
    return_code = "200 OK"
    return response


async def write_writer(writer, response):
    try:
        writer.write(response.encode("utf-8"))  # Cannot be async
        await writer.drain()
        await writer.aclose()
    except Exception as e:
        print(f"Write Error: {e}")


async def handle_client(reader, writer):
    if DEBUG:
        increment()
        print(f"Running: {counter}")

    addr = writer.get_extra_info("peername")
    print(f"Connection from {addr!r}")
    request = await read_reader(reader)
    response = await craft_response(request)
    await write_writer(writer, response)
    print(f"Memory: {free()}")

    if DEBUG:
        decrement()
        print(f"Running: {counter}")


async def main():
    await connect_wifi()
    server = await uasyncio.start_server(handle_client, "0.0.0.0", port)
    print(f"Waiting for connections...")
    while True:
        await uasyncio.sleep(3600)


if __name__ == "__main__":
    try:
        uasyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down NOW...")
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            wlan.disconnect()
        wlan.active(False)
        sys.exit()
