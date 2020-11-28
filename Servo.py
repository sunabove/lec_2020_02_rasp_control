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
        self.HPulse = 0  #Sets the initial Pulse
        self.VPulse = 0  #Sets the initial Pulse 

        self.setPWMFreq(50)
        self.setServoPulse(1, self.VPulse)
        self.setServoPulse(0, self.HPulse)
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
        
        sleep(0.005)
        
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
        # "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse*4096/20000                #PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, 0, int(pulse))
    pass

    def stop_servo(self) :
        print(inspect.currentframe().f_code.co_name)
    pass 

    def stop(self):
        print(inspect.currentframe().f_code.co_name)
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
    import curses

    GPIO.setwarnings(False)

    servo = Servo()

    if False : 
        channel = 0

        for pulse in range(500, 2500, 10):    
            print( f"pulse = {pulse}" )
            servo.setServoPulse(channel, pulse)     
            sleep(0.02)  
        pass
    pass
    
    if False : 
        for channel in range( 2 ) : 
            # setServoPulse(2,2500)
            for i in range(500,2500,10):    
                servo.setServoPulse(channel,i)     
                sleep(0.02)         
            
            for i in range(2500,500,-10):
                servo.setServoPulse(channel,i) 
                sleep(0.02)
            pass
        pass
    pass  

    GPIO.cleanup()   

    actions = {
        curses.KEY_UP:    servo.up,
        curses.KEY_DOWN:  servo.down,
        curses.KEY_LEFT:  servo.left,
        curses.KEY_RIGHT: servo.right,
    }

    def main(window):
        next_key = None
        go_on = True

        while go_on :
            curses.halfdelay(1)
            if next_key is None:
                try : 
                    key = window.getch()
                except KeyboardInterrupt :
                    go_on = False
                pass
            else:
                key = next_key
                next_key = None
            pass

            if go_on and key != -1:
                # KEY PRESSED
                curses.halfdelay(3)
                action = actions.get(key)
                if action is not None:
                    action()
                next_key = key
                while next_key == key:
                    next_key = window.getch()
                pass 
            pass
        pass
    pass

    curses.wrapper(main) 
pass    
