# Captive Portal!
#
# Blame: helmut.doring@slug.org
#

from machine import Pin, PWM
from neopixel import NeoPixel

import usocket as socket

import gc

gc.collect()
gc.enable()

import sys

import network
import uasyncio as asyncio

ONBOARD_RGB_LED_PIN = 8

HTTP_PORT = 80
DNS_PORT = 53
BIND_IFACE = "0.0.0.0"

HTML_FILE = "demon.html"

# Access point settings
SERVER_SSID = "👹 - Password: 123456789"  # max 32 characters
SERVER_PASS = "123456789"
SERVER_IP = "10.11.12.13"
SERVER_SUBNET = "255.255.255.0"


def turn_off_led(P):
    pin = Pin(P, Pin.OUT)
    led = NeoPixel(pin, 1)
    led[0] = (0, 0, 0)
    led.write()


def free():
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = "{0:.2f}%".format(F / T * 100)
    return "Total:{0} Free:{1} ({2})".format(T, F, P)


def swap_boot(script):
    fname = "/captive_portal/" + script
    f = open(fname)
    data = f.read()
    f.close()
    f = open("/boot.py", "w")
    f.write(data)
    f.close()


# 20dB is 100mW, but my XAIO Seeed S3 says 73mW which is ~18.5dB.
# 15dB (60mW) may be BETTER!
def wifi_start_access_point():
    wifi = network.WLAN(network.AP_IF)
    wifi.active(True)
    wifi.ifconfig((SERVER_IP, SERVER_SUBNET, SERVER_IP, SERVER_IP))
    wifi.config(
        essid=SERVER_SSID,
        channel=3,
        authmode=network.AUTH_WPA_WPA2_PSK,  # AUTH_OPEN for no auth
        password=SERVER_PASS,
        txpower=15,
        pm=network.WLAN.PM_PERFORMANCE,
    )
    print("Network config:", wifi.ifconfig())


# uasyncio v3 exception handler
def _handle_exception(loop, context):
    sys.print_exception(context["exception"])
    sys.exit()


class DNSQuery:
    def __init__(self, data):
        if "google" in data:
            raise Exception("Dropping query from Google!")

        self.data = data
        self.domain = ""
        tipo = (data[2] >> 3) & 15  # Opcode bits
        if tipo == 0:  # Standard query
            ini = 12
            lon = data[ini]
            while lon != 0:
                self.domain += data[ini + 1 : ini + lon + 1].decode("utf-8") + "."
                ini += lon + 1
                lon = data[ini]
        print("DNS query: " + self.domain)

    def response(self, ip):
        print("DNS reply: {} ==> {}".format(self.domain, ip))
        packet = self.data[:2] + b"\x81\x80"
        packet += (
            self.data[4:6] + self.data[4:6] + b"\x00\x00\x00\x00"
        )  # Questions and Answers Counts
        packet += self.data[12:]  # Original Domain Name Question
        packet += b"\xc0\x0c"  # Pointer to domain name
        # response type, ttl, and data length (4 bytes)
        packet += b"\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04"
        packet += bytes(map(int, ip.split(".")))  # 4bytes of IP
        return packet


class MyApp:
    async def start(self):
        # Get the event loop
        loop = asyncio.get_event_loop()

        # Add global exception handler
        loop.set_exception_handler(_handle_exception)

        # Start the wifi AP
        wifi_start_access_point()

        # Create the server and add task to event loop
        server = asyncio.start_server(
            self.handle_http_connection, BIND_IFACE, HTTP_PORT
        )
        loop.create_task(server)

        # Start the DNS server task
        loop.create_task(self.run_dns_server())

        # Start looping forever
        print("BEGIN loop")
        loop.run_forever()

    async def handle_http_connection(self, reader, writer):
        # Get HTTP request line
        data = await reader.readline()
        request_line = data.decode()
        addr = writer.get_extra_info("peername")
        print("Received: {} from {}".format(request_line.strip(), addr))

        # Read and discard header data
        while True:
            line = await reader.readline()
            if line == b"\r\n":
                break

        # Handle request
        if len(request_line) > 0:
            response = "HTTP/1.1 200 OK\r\n\r\n"
            with open(HTML_FILE) as f:
                response += f.read()
            await writer.awrite(response)

        # Close socket
        await writer.aclose()
        print("Memory: " + free())

    # DNS request handler
    async def run_dns_server(self):
        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.setblocking(False)
        udps.bind((BIND_IFACE, DNS_PORT))

        while True:
            try:
                yield asyncio.core._io_queue.queue_read(udps)
                data, addr = udps.recvfrom(4096)

                DNS = DNSQuery(data)
                udps.sendto(DNS.response(SERVER_IP), addr)

            except Exception as e:
                print("DNS error: ", e)
                await asyncio.sleep_ms(3000)

        udps.close()


### Main ###
turn_off_led(ONBOARD_RGB_LED_PIN)

try:
    # Instantiate app and run
    myapp = MyApp()
    asyncio.run(myapp.start())
except Exception as e:
    print("Exception:", type(e).__name__, "–", e)
finally:
    asyncio.new_event_loop()  # Clear state
