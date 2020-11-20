# coding: utf-8

import threading
import time
import math
import smbus

import RPi.GPIO as GPIO

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class Servo :

    # Registers/etc.
    __SUBADR1          = 0x02
    __SUBADR2          = 0x03
    __SUBADR3          = 0x04
    __MODE1            = 0x00
    __PRESCALE         = 0xFE
    __LED0_ON_L        = 0x06
    __LED0_ON_H        = 0x07
    __LED0_OFF_L       = 0x08
    __LED0_OFF_H       = 0x09
    __ALLLED_ON_L      = 0xFA
    __ALLLED_ON_H      = 0xFB
    __ALLLED_OFF_L     = 0xFC
    __ALLLED_OFF_H     = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685") 
        self.write(self.__MODE1, 0x00)

        #Set servo parameters
        self.HPulse = 1500  #Sets the initial Pulse
        self.HStep = 0      #Sets the initial step length
        self.VPulse = 1500  #Sets the initial Pulse
        self.VStep = 0      #Sets the initial step length

        if False : 
            self.setPWMFreq(50)
            self.setServoPulse(1, self.VPulse)
            self.setServoPulse(0, self.HPulse)
        pass

        self.timerfunc()
    pass
	
    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
        pass
    pass

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        pass

        return result
    pass

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0        # 25MHz
        prescaleval /= 4096.0             # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        pass
    
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)
        pass

        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10                # sleep
        self.write(self.__MODE1, newmode)                # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)
    pass

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)
        
        if (self.debug):
            print("channel: %d    LED_ON: %d LED_OFF: %d" % (channel,on,off))
        pass
    pass
	    
    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse*4096/20000                #PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, 0, int(pulse))
    pass

    def stop_servo(self) :
        self.HStep = 0 
        self.VPulse = 0 
    pass

    def timerfunc(self):
        #print( "timerfunc" )

        if(self.HStep != 0):
            self.HPulse += HStep

            if(self.HPulse >= 2500): 
                self.HPulse = 2500
            elif(self.HPulse <= 500):
                self.HPulse = 500
            pass

            #set channel 2, the Horizontal servo
            self.setServoPulse(0,HPulse)
        pass
            
        if(self.VStep != 0):
            self.VPulse += VStep

            if(self.VPulse >= 2500): 
                self.VPulse = 2500
            elif(self.VPulse <= 500):
                self.VPulse = 500
            pass

            #set channel 3, the vertical servo
            self.setServoPulse(1,VPulse)
        pass

        self.t = threading.Timer(0.02, self.timerfunc)
        #self.t.setDaemon(True)
        self.t.start()
    pass
pass

if __name__=='__main__':
    GPIO.setwarnings(False)

    servo = Servo()
    servo.setPWMFreq(50)

    servo.setServoPulse(0,1500)
    time.sleep(1)
    servo.setServoPulse(1,2000)
    time.sleep(1)

    for channel in range( 2 ) : 
        # setServoPulse(2,2500)
        for i in range(500,2500,10):    
            servo.setServoPulse(channel,i)     
            time.sleep(0.02)         
        
        for i in range(2500,500,-10):
            servo.setServoPulse(channel,i) 
            time.sleep(0.02)
        pass
    pass

    servo.setServoPulse(0,1500)
    time.sleep(1)
    servo.setServoPulse(1,2000)
    time.sleep(1)

    servo.setServoPulse(0,0)
    servo.setServoPulse(1,0)
    time.sleep(1)

    GPIO.cleanup()    
pass    
