#coding: utf-8
import RPi.GPIO as GPIO, inspect
from time import sleep

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class Motor:

    def __init__(self, ain1=12, ain2=13, ena=6, bin1=20, bin2=21, enb=26):
        self.AIN1 = ain1; self.AIN2 = ain2; self.ENA = ena
        self.BIN1 = bin1; self.BIN2 = bin2; self.ENB = enb
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for port in [ ain1, ain2, ena, bin1, bin2, enb ] : 
            GPIO.setup(port,GPIO.OUT)
        pass

        self.PWMA = GPIO.PWM(ena,500)
        self.PWMB = GPIO.PWM(enb,500)

        self._speed = 10  

        self.PWMA.start( self._speed )
        self.PWMB.start( self._speed ) 

    pass

    def __del__( self ) :
        self.finish()
    pass

    def finish(self) : 
        log.info(inspect.currentframe().f_code.co_name)

        self._speed = 0 

        if hasattr( self, "PWMA" ) : 
            self.PWMA and self.PWMA.stop()
        pass

        if hasattr( self, "PWMB") :
            self.PWMB and self.PWMB.stop(0)
        pass

        self.PWMA = None
        self.PWMB = None

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for port in [ self.AIN1, self.AIN2, self.ENA, self.BIN1, self.BIN2, self.ENB ] : 
            GPIO.cleanup(port)
        pass
    pass

    def setMotor(self, left = 0, right =0):
        self.setGPIO_PWM( self.AIN1, self.AIN2, self.PWMA, left )
        self.setGPIO_PWM( self.BIN1, self.BIN2, self.PWMB, right )
    pass

    def setGPIO_PWM( self, ain1, ain2, pwma, value ) : 
        value = 100 if value > 100 else value 
        value = -100 if value < -100 else value 

        if value > 0 :
            GPIO.output(ain1,GPIO.LOW)
            GPIO.output(ain2,GPIO.HIGH)
            pwma.ChangeDutyCycle(value)
        elif value < 0 :
            GPIO.output(ain1,GPIO.HIGH)
            GPIO.output(ain2,GPIO.LOW)
            pwma.ChangeDutyCycle( - value)
        else :
            pwma.ChangeDutyCycle( 0 )
            GPIO.output(ain1,GPIO.LOW)
            GPIO.output(ain2,GPIO.LOW)
        pass 
    pass

    def speed_up(self, dv) : # 속도 증가 
        _speed = self._speed = + dv
        if _speed < 0 :
            _speed = 0 
        elif _speed > 100 :
            _speed = 100
        pass

        self._speed = _speed
    pass # -- speed_up

    def forward(self, left=None, right=None): # 전진
        log.info(inspect.currentframe().f_code.co_name) 

        if left is None : 
            left = self._speed 
        pass

        if right is None :
            right = left
        pass

        self.setMotor( left, right)
    pass

    def backward(self, left=None, right=None):  # 후진
        log.info(inspect.currentframe().f_code.co_name)
        
        if left is None : 
            left = self._speed 
        pass

        if right is None :
            right = left
        pass
    
        self.setMotor( -left, -right)
    pass

    def back(self, left=None, right=None): # 후진 
        self.backward(left, right)
    pass

    def stop(self):
        log.info(inspect.currentframe().f_code.co_name)

        self.setMotor( 0, 0 )
    pass

    def stop_motor(self):
        log.info(inspect.currentframe().f_code.co_name)

        self.setMotor( 0, 0 )
    pass

    def left(self):
        log.info(inspect.currentframe().f_code.co_name)

        speed = self._speed

        self.setMotor( - speed, speed )
    pass

    def right(self):
        log.info(inspect.currentframe().f_code.co_name)

        speed = self._speed
        self.setMotor( speed, - speed )
    pass

    def test_all(self, duration=3) :    
        self.forward()
        sleep(duration)
        self.backward()
        sleep(duration)
        self.left()
        sleep(duration)
        self.right()
        sleep(duration)
        self.stop()
    pass

pass

if __name__=='__main__':
    log.info( "Hello" )

    GPIO.setwarnings(False)
    
    motor = Motor()

    try:
        motor.test_all(duration=3)        
    except KeyboardInterrupt:
        print( "" )
    pass 
    
    motor.finish()
    
    sleep( 0.5 )

    GPIO.cleanup()

    log.info( "Good bye!" )
pass
