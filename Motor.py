#coding: utf-8
import RPi.GPIO as GPIO, inspect
from time import sleep, time
from math import sqrt

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class Motor:

    def __init__(self, ain1=12, ain2=13, ena=6, bin1=20, bin2=21, enb=26, debug=False):
        self.debug = debug

        self.AIN1 = ain1; self.AIN2 = ain2; self.ENA = ena
        self.BIN1 = bin1; self.BIN2 = bin2; self.ENB = enb
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for port in [ ain1, ain2, ena, bin1, bin2, enb ] : 
            GPIO.setup(port,GPIO.OUT)
        pass

        self.PWMA = GPIO.PWM(ena, 500)
        self.PWMB = GPIO.PWM(enb, 500)

        self._min_speed = 10

        self._speed_left  = self._min_speed  
        self._speed_right = self._min_speed  

        self.mode = "stop"

        self.PWMA.start( self._speed_left )
        self.PWMB.start( self._speed_right ) 

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
            GPIO.setmode(GPIO.BCM)
            GPIO.cleanup(port)
        pass
    pass

    def setMotor(self, left = 0, right =0):
        self._speed_left = left
        self._speed_right = right
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

            pwma.ChangeDutyCycle( abs(value) )
        elif value == 0 :
            GPIO.output(ain1,GPIO.LOW)
            GPIO.output(ain2,GPIO.LOW)

            pwma.ChangeDutyCycle( 0 ) 
        pass 
    pass

    def speed_down(self, dv = 5) : # 속도 증가
        self.speed_up( -dv )
    pass

    def speed_up(self, dv = 5) : # 속도 증가

        left = self._speed_left + dv
        
        if left < -100 :
            left = -100 
        elif left > 100 :
            left = 100
        pass

        right = self._speed_right + dv
        
        if right < -100 :
            right = -100 
        elif right > 100 :
            right = 100
        pass

        self.setMotor( left, right )
    pass # -- speed_up

    def forward(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.HIGH)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.HIGH)
    pass

    def stop(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.LOW)
    pass

    def back(self) :
        self.backward()
    pass

    def backward(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.AIN1,GPIO.HIGH)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.HIGH)
        GPIO.output(self.BIN2,GPIO.LOW)
    pass 
        
    def left(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.PWMA.ChangeDutyCycle(30)
        self.PWMB.ChangeDutyCycle(30)
        GPIO.output(self.AIN1,GPIO.HIGH)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.HIGH)
    pass 

    def right(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.PWMA.ChangeDutyCycle(30)
        self.PWMB.ChangeDutyCycle(30)
        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.HIGH)
        GPIO.output(self.BIN1,GPIO.HIGH)
        GPIO.output(self.BIN2,GPIO.LOW)
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
    
    motor = Motor(debug=True)

    try:
        motor.test_all(duration=3)        
    except KeyboardInterrupt:
        print( "" )
    pass 
    
    motor.finish()
    
    sleep( 0.5 )

    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()

    log.info( "Good bye!" )
pass
