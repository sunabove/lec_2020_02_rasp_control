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

        self.min_speed = 5
        self.turn_speed = 15

        self.PA = self.min_speed  
        self.PB = self.min_speed  

        self.mode = "stop"

        self.PWMA.start( self.PA )
        self.PWMB.start( self.PA ) 

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

    def speed_down(self, dv = 5) : # 속도 증가
        self.speed_up( -dv )
    pass

    def speed_up(self, dv = 5) : # 속도 증가

        mode = self.mode

        log.info( f"before PA = {self.PA}, right={self.PB}, dv={dv}")

        if mode == "stop" :
            return 
        pass

        left = self.PA + dv
        
        if left < 0 :
            left = 0 
        elif left > 100 :
            left = 100
        pass

        self.PA = left

        right = self.PB + dv
        
        if right < 0 :
            right = 0 
        elif right > 100 :
            right = 100
        pass

        self.PB = right

        log.info( f"after PA = {self.PA}, right={self.PB}, dv={dv}")

        if self.PA == 0 and self.PB == 0 :
            self.stop()
        elif mode =="forward" :
            self.forward()
        elif mode == "backward" :
            self.backward()
        elif mode == "left" :
            self.left()
        elif mode == "right" :
            self.right()
        elif mode == "stop" :
            self.stop()
        pass
    pass # -- speed_up

    def forward(self, left = None, right=None):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "forward"
        min_speed = self.min_speed 

        if left is not None and right is None :
            right = left
        pass

        self.PA = self.PA if left is None else left
        self.PB = self.PB if right is None else right

        self.PA = self.PA if self.PA > min_speed else min_speed 
        self.PB = self.PB if self.PB > min_speed else min_speed  

        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)

        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.HIGH)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.HIGH)
    pass

    def backward(self, left=None, right=None):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "backward"
        min_speed = self.min_speed

        if left is not None and right is None :
            right = left
        pass

        self.PA = self.PA if left is None else left
        self.PB = self.PB if right is None else right

        self.PA = self.PA if self.PA > min_speed else min_speed 
        self.PB = self.PB if self.PB > min_speed else min_speed  

        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.AIN1,GPIO.HIGH)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.HIGH)
        GPIO.output(self.BIN2,GPIO.LOW)
    pass 
        
    def left(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "left"

        turn_speed = self.turn_speed

        self.PWMA.ChangeDutyCycle(turn_speed)
        self.PWMB.ChangeDutyCycle(turn_speed)
        
        GPIO.output(self.AIN1,GPIO.HIGH)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.HIGH)
    pass 

    def right(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "right"

        turn_speed = self.turn_speed

        self.PWMA.ChangeDutyCycle(turn_speed)
        self.PWMB.ChangeDutyCycle(turn_speed)
        
        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.HIGH)
        GPIO.output(self.BIN1,GPIO.HIGH)
        GPIO.output(self.BIN2,GPIO.LOW)
    pass

    def stop(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "stop"

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
