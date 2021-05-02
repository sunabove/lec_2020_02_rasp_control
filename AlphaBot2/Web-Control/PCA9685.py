#!/usr/bin/python

import math, smbus
from time import sleep

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:

    # Registers/etc.
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if self.debug :
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)
    pass

    def write(self, reg, value):
        # "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if self.debug :
            0 and print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
      
    def read(self, reg):
        # "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if self.debug :
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        # "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if self.debug :
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if self.debug :
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, off):
        # "Sets a single PWM channel"
        off = int( off )

        self.write(self.__LED0_ON_L+4*channel, 0x00 )
        self.write(self.__LED0_ON_H+4*channel, 0x00 )
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)
        self.debug and print( f"channel: {channel}; LED_OFF: {off}" ) 
    pass
      
    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, pulse)
    pass
pass

if __name__=='__main__':
    try :
        pwm = PCA9685(debug=1)
        pwm.setPWMFreq(50)
        if 1 :
            channel = 0 
            init = 80
            min = 118   
            max = 130
            step = 1            
            pwm.setPWM(channel, init)
            sleep( 5 )
            pwm.setServoPulse( channel, 0 )
            duration = 0.2
            for i in range( min, max + 1, step ):  
                pwm.setPWM(channel, i)   
                sleep( duration ) 
            pass
            
            pwm.setServoPulse( channel, 0 )
            sleep( 1 )

            for i in range( max, init - 1, - step ):  
                pwm.setPWM(channel, i)   
                sleep( duration ) 
            pass
        pass
    except : 
        pass
    finally:
        pwm.setServoPulse( 0, 0 )
        pwm.setServoPulse( 1, 0 )
    pass

pass
