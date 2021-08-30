import network
import ujson
import urequests

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('AP47', '84218421*')
while not sta_if.isconnected():
    pass

r = urequests.get("https://blockchain.info/ru/ticker")
js = ujson.loads(r.content)
r.close()

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

i2c = I2C(scl=Pin(5), sda=Pin(4))
oled = SSD1306_I2C(128, 32, i2c)

oled.text('BTC:' + str(js["RUB"]["last"]) + ' RUB',0,0)
oled.show()
sta_if.disconnet()
