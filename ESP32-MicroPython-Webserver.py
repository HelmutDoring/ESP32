import sys, time, socket, select, network, ubinascii, uasyncio

port = 8080
ssid = "MyRouter"
password = "MyPassword"
myip = "192.168.1.111"
netmask = "255.255.255.0"
gateway = "192.168.1.254"
dnshost = gateway


async def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.config(txpower=15)
    if sta_if.isconnected():
        sta_if.disconnect()
        print(f"started in the connected state, but now disconnected")
    else:
        print(f"started in the disconnected state")
    if not sta_if.isconnected():
        print("Connecting to network...")
        try:
            sta_if.connect(ssid, password)
        except Exception as e:
            print(f"Error: {e}")
        # pass a 4-tuple!
        sta_if.ifconfig((myip, netmask, gateway, dnshost))
        while not sta_if.isconnected():
            await uasyncio.sleep_ms(100)
    mac = ubinascii.hexlify(sta_if.config("mac"), ":").decode()
    print(f"MAC ADDRESS: {mac}")
    print("IP ADDRESS: ", sta_if.ifconfig()[0])


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connection from {addr!r}")

    data = await reader.read(1024)
    reader.close()
    reader.wait_closed()
    message = data.decode()
    print(f"Received: {message!r}")

    response = (
        "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello from ESP32!\r\n"
    )
    writer.write(response.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    print("Responded!")


async def main():
    await connect_wifi()

    loop = uasyncio.get_event_loop()
    server = await uasyncio.start_server(handle_client, "0.0.0.0", port)
    loop.run_forever()


if __name__ == "__main__":
    uasyncio.run(main())
