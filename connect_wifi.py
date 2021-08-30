import network
import time
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wi-Fi', '15721572')

counter = 15
while not sta_if.isconnected():
    time.sleep(1)
    counter-=1
    if not counter:
        print("Can't connect to wi-fi network")
        machine.deepsleep()
		
print("Connected to wi-fi network")