import pyb
from lcd import HD44780
import onewire
import time, ds18x20, os

class temperature_sensor:
    def __init__(self, pin):
        self.ow = onewire.OneWire(pyb.Pin(pin))
        self.ds = ds18x20.DS18X20(self.ow)
        self.roms = self.ds.scan()
        self.ds.convert_temp()
        time.sleep_ms(750)
        self.temperature=self.ds.read_temp(self.roms[0])
        self.ds.convert_temp()
        self.last_update_time=pyb.millis()
    
    def temperature_task(self):
        if pyb.millis()-self.last_update_time > 1000:
            self.last_update_time=pyb.millis()
            self.temperature=self.ds.read_temp(self.roms[0])
            self.ds.convert_temp()

    def get_temperature(self):
        return self.temperature
    
class lcd_screen:
    def __init__(self, pins):
        self.lcd=HD44780()
        self.lcd.PINS=pins
        self.lcd.init()
        self.last_update_time=pyb.millis()
        
    def screen_task(self, tc, ts, out):
        if pyb.millis()-self.last_update_time > 100:
            self.last_update_time=pyb.millis()
            self.lcd.set_line(0)
            self.lcd.set_string("Tc={:.1f} Ts={:.0f}".format(tc, ts))
            self.lcd.set_line(1)
            self.lcd.set_string("Output={:.0f}%".format(out))

class pid:
    def __init__(self, P=3, I=0.03, D=0.1, set_point=0.0, value=0.0, out_function=lambda *_, **__: None):
        self.Kp=P
        self.Ki=I
        self.Kd=D
        self.I_value=0  
        self.P_value=0
        self.D_value=0
        self.set_point=set_point
        self.prev_value=value
        self.last_update_time=pyb.millis()
        self.output=0
        self.out_function=out_function
        
    def pidProcess(self,value):
        if pyb.millis()-self.last_update_time > 1000:
            self.last_update_time=pyb.millis()
            error=self.set_point-value
            self.P_value = self.Kp*error
            self.I_value += self.Ki*error
            self.D_value = self.Kd*(self.prev_value - value)
            self.prev_value=value
            if self.P_value>100:
                self.P_value=100
            elif self.P_value<-100:
                self.P_value=-100
            if self.I_value>100:
                self.I_value=100
            elif self.I_value<-100:
                self.I_value=-100
            if self.D_value>100:
                self.D_value=100
            elif self.D_value<-100:
                self.D_value=-100
            out = self.P_value + self.I_value + self.D_value
            if out>100:
                out=100
            elif out<0:
                out=0
            self.output=out
            self.out_function(100-self.output)
            
    def getOutput(self):
        return self.output
        
    def setSetpoint(self,set_point):
        self.I_value=0  
        self.P_value=0
        self.D_value=0
        self.set_point=set_point
        self.last_update_time=pyb.millis()
        self.output=0
          
class logdata:
    def __init__(self):
        self.last_update_time=pyb.millis()
        
    def add(self, data):
        if pyb.millis()-self.last_update_time > 10000:
            self.last_update_time=pyb.millis()
            f=open('log.csv','a')
            f.seek(0, 2) # seek to end
            f.write(str(data))
            f.write('\n')
            f.close




            
try:
    f=open('setpoint.txt', 'rb')
    setpoint=int(f.read())
    f.close()

    t=temperature_sensor('A6')
    l=lcd_screen(['A0','A1','A2','A3','A4','A5'])

    ten=pyb.Pin('B13')
    tim = pyb.Timer(1, freq=1)
    ch = tim.channel(1, pyb.Timer.PWM, pin=ten)
    ch.pulse_width_percent(100)

    p=pid(set_point=setpoint, value=t.get_temperature(), out_function=ch.pulse_width_percent)

    logger=logdata()

    plus_button_state=0
    plus_button_time=pyb.millis()
    plus_button_fast_time=pyb.millis()
    plus_button_pin=pyb.Pin('C6', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
    plus_button_increased=False

    minus_button_state=0
    minus_button_time=pyb.millis()
    minus_button_fast_time=pyb.millis()
    minus_button_pin=pyb.Pin('C7', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
    minus_button_increased=False

    set_point_time=pyb.millis()
    set_point_prev=setpoint
    set_point_rec=setpoint
    need_write_setpoint=False

    while True:
        t.temperature_task()
        l.screen_task(t.get_temperature(), setpoint, p.getOutput())
        p.pidProcess(t.get_temperature())
        logger.add(t.get_temperature())
        #buttons
        if plus_button_pin.value() and not minus_button_pin.value():
            if pyb.millis()-plus_button_time > 50 and plus_button_increased==False:
                plus_button_increased=True
                setpoint=setpoint+1
                if setpoint>120:
                    setpoint=120
            elif pyb.millis()-plus_button_time > 1000:
                if pyb.millis()-plus_button_fast_time > 100:
                    plus_button_fast_time=pyb.millis()
                    setpoint=setpoint+1
                    if setpoint>120:
                        setpoint=120           
        else:
            plus_button_increased=False
            plus_button_time=pyb.millis()
            
        if minus_button_pin.value() and not plus_button_pin.value():
            if pyb.millis()-minus_button_time > 50 and minus_button_increased==False:
                minus_button_increased=True
                setpoint=setpoint-1
                if setpoint<-40:
                    setpoint=-40
            elif pyb.millis()-minus_button_time > 1000:
                if pyb.millis()-minus_button_fast_time > 100:
                    minus_button_fast_time=pyb.millis()
                    setpoint=setpoint-1
                    if setpoint<-40:
                        setpoint=-40           
        else:
            minus_button_increased=False
            minus_button_time=pyb.millis()
            
        if set_point_prev!=setpoint:
            set_point_prev=setpoint
            need_write_setpoint=True
            set_point_time=pyb.millis()
        if need_write_setpoint and pyb.millis()-set_point_time>3000:
            need_write_setpoint=False
            if set_point_rec!=setpoint:
                set_point_rec=setpoint
                p.setSetpoint(setpoint)
                os.remove('setpoint.txt')
                f=open('setpoint.txt', 'wb')
                f.write(str(setpoint))
                f.close()
except:
    ten=pyb.Pin('B13', pyb.Pin.OUT_PP)
    ten.value(False)