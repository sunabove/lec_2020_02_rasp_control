# coding: utf-8

import threading, math, RPi.GPIO as GPIO, smbus, inspect, numpy as np
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

    def __init__(self, address=0x40, debug=0):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        
        if self.debug :
            print("Reseting PCA9685") 
        pass

        self.write(self.__MODE1, 0x00) 
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
        0 and print("I2C: Write 0x%02X to register 0x%02X" % (value, reg)) 
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
        
        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10                # sleep
        self.write(self.__MODE1, newmode)                # go to sleep

        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        
        sleep(0.005)
        
        self.write(self.__MODE1, oldmode | 0x80)
    pass

    def setPWM(self, channel, off):
        self.write(self.__LED0_ON_L+4*channel, 0x00)
        self.write(self.__LED0_ON_H+4*channel, 0x00)

        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)
        
        self.debug and print("channel = %d, pwm = %d" % (channel, off)) 
    pass
    
    def setServoPulse(self, channel, pulse):
        print( f"channel = {channel}, pulse={pulse}" ) 
        
        # "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pwm = pulse*4096/20000 #PWM frequency is 50HZ,the period is 20000us
        pwm = int( pwm )

        self.setPWM(channel, pwm)

        print( f"channel = {channel}, pulse = {pulse}, pwm = {pwm}")
    pass

    def stop_servo(self) :
        self.stop()
    pass

    def stop(self):
        self.debug and print(inspect.currentframe().f_code.co_name)

        self.setPWM(0, 0)
        self.setPWM(1, 0) 
    pass

    def up(self):
        self.debug and print(inspect.currentframe().f_code.co_name)

        channel = 1 
        servo.setPWM(channel, 390 ) 
        sleep( 0.02 ) 
        servo.setPWM(channel, 0)
    pass

    def down(self):
        self.debug and print(inspect.currentframe().f_code.co_name)

        channel = 1
        self.setPWM(channel, 470)
        sleep( 0.02 )
        servo.setPWM(channel, 0)
    pass

    def left(self):
        self.debug and print(inspect.currentframe().f_code.co_name)

        channel = 0  
        self.setPWM(channel, 150 ) 
        sleep( 0.02 ) 
        self.setPWM(channel, 0)
    pass

    def right(self):
        self.debug and print(inspect.currentframe().f_code.co_name)

        channel = 0
        self.setPWM(channel, 105)
        sleep( 0.02 )
        servo.setPWM(channel, 0)
    pass

pass

if __name__=='__main__':
    GPIO.setwarnings(False)

    servo = Servo( debug=0 ) 

    servo.setPWMFreq(50)

    import curses

    actions = {
        curses.KEY_UP:    servo.up,
        curses.KEY_DOWN:  servo.down,
        curses.KEY_LEFT:  servo.left,
        curses.KEY_RIGHT: servo.right,
    }

    def control_servo(window):
        next_key = None
        while True:
            curses.halfdelay(1)
            if next_key is None:
                key = window.getch()
            else:
                key = next_key
                next_key = None
            pass

            if key != -1:
                # KEY PRESSED
                curses.halfdelay(3)
                action = actions.get(key)
                if action is not None:
                    action()
                pass

                next_key = key
                while next_key == key:
                    next_key = window.getch()
                pass
                # KEY RELEASED
                # servo.stop()
            pass
        pass
    pass

    if 1 : 
        curses.wrapper( control_servo )
    pass
    
    try :
        if 0 :         
            channel = 0
            print( f"channel = {channel}" ) 
            servo.debug = 1

            for pwm in range( 50, 200, 5 ) :
                servo.setPWM(channel, pwm)
                sleep( 1 )
            pass
        pass

        if 0 :         
            channel = 0
            print( f"channel = {channel}" )

            print( "Init...." )
            for i in range( 10 ) : 
                servo.right()
                sleep( 1 )
                servo.left()
                sleep( 1 )
            pass
        pass 

        if 0 :         
            channel = 1
            servo.debug = 1
            print( f"channel = {channel}" ) 
            #servo.setServoPulse(1,2000)
            for pwm in range( 300, 430, 5) :
                servo.setPWM(channel, pwm)
                sleep( 1 )
            pass
        pass
    finally :
        servo.stop()
    pass
pass    
