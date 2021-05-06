#!/usr/bin/python
import logging as log, time, math, smbus

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

    ROLL_MIN = 750
    ROLL_MID = 1750
    ROLL_MAX = 2750
    ROLL_DEG = (ROLL_MAX - ROLL_MIN) / 180.0
    
    PITCH_MIN = 1150
    PITCH_MID = 2100
    PITCH_MAX = 2800
    PITCH_DEG = (PITCH_MAX - PITCH_MIN) / 180.0

    MIN_MID_MAX_DEGS = ( ( ROLL_MIN, ROLL_MAX, ROLL_DEG ), (PITCH_MIN, PITCH_MAX, PITCH_DEG) )

    def __init__(self, address=0x40, debug=False):
        log.basicConfig( format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
            )
        self.log = log.getLogger( self.__class__.__name__ )

        self.bus = smbus.SMBus(1)
        self.address = address
        self.log.debug("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)
    pass
	
    def write(self, reg, value):
        # "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        self.log.debug("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
    def read(self, reg):
        # "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        self.log.debug("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result
    pass

    def setPWMFreq(self, freq):
        # "Sets the PWM frequency"
        self.freq = freq
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        
        self.log.debug("Setting PWM frequency to %d Hz" % freq)
        self.log.debug("Estimated pre-scale: %d" % prescaleval)
        
        prescale = math.floor(prescaleval + 0.5)
        self.log.debug("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10        # sleep

        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)
    pass

    def setPWM(self, channel, off):
        #"Sets a single PWM channel"
        on = 0 
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)

        self.log.info( f"channel: {channel}, pwm={off}, LED_ON: {on} LED_OFF: {off}" )
    pass

    def setServoPulse(self, channel, pulse):
        #"Sets the Servo Pulse,The PWM frequency must be 50HZ"
        # pulse * 4096 / 20000
        # PWM frequency is 50HZ,the period is 20000us

        self.log.info( f"pulse = {pulse}" )

        pwm = int( pulse * 4096 * self.freq / 1000000 )
        self.setPWM( channel, pwm )
    pass
        
    def stop(self, channel):
        self.log.debug("Stopping PCA9685")
        self.write(self.__MODE1, 0x00)
        self.write(self.__PRESCALE, 0x00)
        self.setPWM(channel, 0)
    pass
pass

if __name__=='__main__':
 
    pwm = PCA9685(0x40, debug=True)
    pwm.setPWMFreq(50)
    pwm.setServoPulse(0, 0)   
    pwm.setServoPulse(1, 0)   

    try :
        min = 500
        max = 550
        step = 10
        for channel in [ 0 ] : 
            for i in range( min, max, step):  
                pwm.setServoPulse(channel, i)   
                time.sleep(0.2)
            pass
            
            for i in range( max, min, -step):
                pwm.setServoPulse(channel, i) 
                time.sleep(0.2) 
            pass
        pass
    finally:
        pwm.setServoPulse(0, 0)
        pwm.setServoPulse(1, 0)
        pwm.stop(0)
        pwm.stop(1)
    pass
pass