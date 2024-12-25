try:
    import usocket as socket
except:
    import socket

import network

import esp

esp.osdebug(None)

from time import sleep

import gc

gc.collect()
gc.enable()

ssid = "🚕 - Password: 123456789"
password = "123456789"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(
    essid=ssid,
    channel=3,
    authmode=network.AUTH_WPA_WPA2_PSK,
    password=password,
)

while ap.active() == False:
    sleep(1)

print("AP is active")
print(ap.ifconfig())


def web_page():
    html = """
              <html>
                <head>
                  <style>
                    body { background-color: black; }
                    h1 { display: inline-block; }
                    .h1red { color: red; }
                    .h1green { color: green; }
                    .taxi { color: yellow; }
                  </style>
                  <title>🚕</title>
                </head>
                <body>
                  <h1 class="h1green">Are YOU&nbsp;</h1>
                  <h1 class="h1red">Talkin&apos; to ME?!</h1>
                  <pre class="taxi">
                  >["]<
              .----' '------.
             //^^^^;;^^^^^^^`|
     _______//_____||_____() |________
    /826    :      : ___              )
   (>== ____;======;  |/\><| ==____===<)
  {____/    \_________________/    \__}
       \ '' /                 \ '' /
        '--'                   '--'
                  </pre>
                </body>
              </html>
           """
    return html


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 80))
s.listen(5)


while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
    print("Connection from: ", addr, conn, request)
    response = web_page()
    conn.send(response)
    conn.close()
