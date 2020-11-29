# coding: utf-8

import threading, math, RPi.GPIO as GPIO, smbus, inspect

from time import sleep

class Servo :
    # ============================================================================
    # Raspi PCA9685 16-Channel PWM Servo Driver
    # ============================================================================

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
        
        if self.debug :
            print("Reseting PCA9685") 
        pass

        self.write(self.__MODE1, 0x00)

        #Set servo parameters
        self.VStep = 0 
        self.HStep = 0 
        
        self.hpulse = 680  #Sets the initial Pulse
        self.vpulse = 680  #Sets the initial Pulse  
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        self.stop()
    pass
	
    def write(self, reg, value):
        #"Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
        pass
    pass

    def read(self, reg):
        #"Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        pass

        return result
    pass

    def setPWMFreq(self, freq):
        # "Sets the PWM frequency"
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
        
        sleep(0.005)
        
        self.write(self.__MODE1, oldmode | 0x80)
    pass

    def _setPWM(self, channel, off):
        #"Sets a single PWM channel"

        on = 0
        
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)

        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)
        
        if (self.debug):
            print("channel: %d    LED_ON: %d LED_OFF: %d" % (channel,on,off))
        pass
    pass
    
    def setServoPulse(self, channel, pulse):
        # "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pwm = pulse*4096//20000 #PWM frequency is 50HZ,the period is 20000us
        self._setPWM(channel, pwm)

        print( f"channel = {channel}, pulse = {pulse}, pwm = {pwm}")
    pass

    def stop_servo(self) :
        self.stop()
    pass

    def stop(self):
        print(inspect.currentframe().f_code.co_name)

        self.setServoPulse(0, 0)
        self.setServoPulse(1, 0)
    pass

    def up(self):
        print(inspect.currentframe().f_code.co_name)
    pass

    def down(self):
        print(inspect.currentframe().f_code.co_name)
    pass

    def left(self):
        print(inspect.currentframe().f_code.co_name)
    pass

    def right(self):
        print(inspect.currentframe().f_code.co_name)
    pass

pass

if __name__=='__main__':
    GPIO.setwarnings(False)

    servo = Servo( debug=False ) 

    servo.setPWMFreq(50)
    #servo.setServoPulse(0,1000)
    #servo.setServoPulse(1,2000)  
    sleep( 1 )

    print( "test" )

    if 0 :         
        channel = 1
        print( f"channel = {channel}" )

        fr = 600 ; to = 800; step = 10 if to > fr else -10
        duration = 0.02
        for pulse in range( fr, to, step ):
            servo.setServoPulse(channel, pulse)
            sleep( duration )  
        pass
    pass

    if 1 :         
        channel = 1
        print( f"channel = {channel}" ) 

        fr = 800 ; to = 600; step = 10 if to > fr else -10
        duration = 0.02
        for pulse in range( fr, to, step ):
            servo.setServoPulse(channel, pulse)
            sleep( duration )  
        pass
    pass

    if 0 : 
        channel = 1
        print( f"channel = {channel}" )

        for pulse in range( 1_000, 600, -10 ):     
            servo.setServoPulse(channel, pulse)     
            sleep( 1 )  
        pass
    pass

    sleep( 2 )

    servo.setServoPulse(0,0)
    servo.setServoPulse(1,0)  

    GPIO.cleanup()
pass    
