import machine

rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
rtc.alarm(rtc.ALARM0, 1*60*1000)

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

bmp_power = machine.Pin(3, machine.Pin.OUT)
bmp_power.on()

from bmp280 import BMP280
bus = machine.I2C(sda=machine.Pin(0),scl=machine.Pin(2))
if not bus.scan():
    print("Can't find BMP280 sensor")
    machine.deepsleep()
    
bmp = BMP280(bus)

t_curr=str(bmp.temperature)
p_curr=str(bmp.pressure)
bmp_power.off()
print("Temperature: " + t_curr)
print("Pressure: " + p_curr)

from umqtt.simple import MQTTClient
client=MQTTClient(client_id='2c:3a:e8:0d:aa:49', server='m11.cloudmqtt.com', port=19909, user='vtbgyrrc', password='e5_L_G08u2-I')

try:
    client.connect()
except:
    print("Can't connect to MQTT server")
    machine.deepsleep()
client.publish('test/t', t_curr)
client.publish('test/p', p_curr)
time.sleep(1)
machine.deepsleep()

