import machine, bme280, ssd1306, time, math, network, socket
def get_values(bme):
i2c_bme = machine.I2C(scl=machine.Pin(12), sda=machine.Pin(14))
oled = ssd1306.SSD1306_I2C(128, 32, i2c_ssd)
while True:

