import network
import socket
import time
import machine
import ssd1306
from umqtt.simple import MQTTClient

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

#internal led on
machine.Pin(2,machine.Pin.OUT)

rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
rtc.alarm(rtc.ALARM0, 5*60*1000)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
#sta_if.connect('eidos424', 'robotech424')
sta_if.connect('eidos308', '21&eidos')

counter = 15
while not sta_if.isconnected():
    time.sleep(1)
    counter-=1
    if not counter:
        oled.text('No wi-fi',0,0)
        oled.show()
        print("Can't connect to MQTT server")
        print("Can't connect to wi-fi network")
        machine.deepsleep()

url='http://stc.oooeidos.ru/presence.php'
_, _, host, path = url.split('/', 3)
try:
    addr = socket.getaddrinfo(host, 80)[0][-1]
except:
    print("Can't get address")
    machine.deepsleep()


s = socket.socket()
s.settimeout(3.0)
try:
    s.connect(addr)
except:
    print("Can't connect to webserver")
    machine.deepsleep()


s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
sitedata = []
while True:
    try:
        data = s.recv(100)
    except:
        print("Can't recv data")
        machine.deepsleep()
        print("Can't receive data from webserver")
    if data:
        sitedata.append(data)
    else:
        break
s.close()

people_cnt=0
for i in range(len(sitedata)):
    tmp_str=str(sitedata[i])
    if i+1 != len(sitedata):
        tmp_str1=str(sitedata[i+1])
        tmp_str=tmp_str[2:-1]
        tmp_str1=tmp_str1[2:14]
        if not tmp_str1.count('<tr><td>'):
            sum_str=tmp_str+tmp_str1[:12]
        else:
            sum_str=tmp_str
    else:
        sum_str=tmp_str
    people_cnt+=sum_str.count('<tr><td>') - sum_str.count('<tr><td></td>')

del sitedata
people=str(people_cnt)

oled.fill(0)
oled.text('In EIDOS now',0,0)
oled.text(people,0,8)
oled.text('people',0,16)
oled.show()
client=MQTTClient(client_id='2c:3a:e8:0d:aa:49', server='narodmon.ru', port=1883, user='dinartal', password='15831')
try:
    client.connect()
except:
    print("Can't connect to MQTT server")
    machine.deepsleep()
client.publish('dinartal/esp8266/people', people)
time.sleep(1)
machine.deepsleep()
