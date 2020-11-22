#coding: utf-8
import RPi.GPIO as GPIO
from time import sleep
import inspect

class Motor:

    def __init__(self,ain1=12,ain2=13,ena=6,bin1=20,bin2=21,enb=26):
        self.AIN1 = ain1; self.AIN2 = ain2; self.ENA = ena
        self.BIN1 = bin1; self.BIN2 = bin2; self.ENB = enb
        self.PA  = 50 ; self.PB  = 50       

        self.clear()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for port in [ ain1, ain2, ena, bin1, bin2, enb ] : 
            GPIO.setup(port,GPIO.OUT)
        pass

        self.PWMA = GPIO.PWM(ena,500)
        self.PWMB = GPIO.PWM(enb,500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        
        self.stop()
    pass

    def __del__( self ) :
        self.clear()
    pass

    def clear(self) :
        print(inspect.currentframe().f_code.co_name)

        if hasattr( self, "PWMA" ) : 
            self.PWMA.stop()
        pass

        if hasattr( self, "PWMB") :
            self.PWMB.stop()
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

    def forward(self, left=50, right=50):
        print(inspect.currentframe().f_code.co_name)
        self.setMotor( left, right)
    pass

    def backward(self, left=50, right=50):
        print(inspect.currentframe().f_code.co_name)
        self.setMotor( -left, -right)
    pass

    def back(self, left=50, right=50):
        self.backward(left, right)
    pass

    def stop(self):
        print(inspect.currentframe().f_code.co_name)
        self.setMotor( 0, 0 )
    pass

    def stop_motor(self):
        self.stop()
    pass

    def left(self):
        print(inspect.currentframe().f_code.co_name)
        self.setMotor( -30, 30 )
    pass

    def right(self):
        print(inspect.currentframe().f_code.co_name)
        self.setMotor( 30, -30 )
    pass

pass

if __name__=='__main__':
    GPIO.setwarnings(False)
    
    motor = Motor()

    try:
        duration = 3
    
        motor.forward()
        sleep(duration)
        motor.backward()
        sleep(duration)
        motor.left()
        sleep(duration)
        motor.right()
        sleep(duration)
        
    except KeyboardInterrupt:
        print( "" )
    pass

    motor.stop()
    sleep(0.5)
    motor.clear()
    sleep( 0.5 )
    GPIO.cleanup()

    print( "Good bye!" )
pass
