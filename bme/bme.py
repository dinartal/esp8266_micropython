import machine
import bme280
import ssd1306
import time
import math

def get_values(bme):
	t, p, h = bme.read_compensated_data()
	
	t = t / 100
	p = p / 34130
	rh = h // 1024 + (h % 1024) / 100
        ah = 6.112 * math.exp( 17.67*t / (t + 243.5)  ) * rh * 2.1674 / (273.15 + t)
		
	return (t, p, rh, ah)
	

i2c_bme = machine.I2C(scl=machine.Pin(12), sda=machine.Pin(14))
i2c_ssd = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))

oled = ssd1306.SSD1306_I2C(128, 32, i2c_ssd)
bme = bme280.BME280(i2c=i2c_bme)

while True:
    oled.fill(0)
    vals = get_values(bme)
	
    oled.text( "TEMP: {} C".format( vals[0] ), 0, 0 )
    oled.text( "PRES: {} mm".format( vals[1] ), 0, 8 )
    oled.text( "RH: {} %".format( vals[2] ), 0, 16)
    oled.text( "AH: {} g/m3".format( vals[3]), 0, 24)
    oled.show()
    time.sleep(1)

