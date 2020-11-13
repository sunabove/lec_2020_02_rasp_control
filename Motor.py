#coding: utf-8
import RPi.GPIO as GPIO
import time

class Motor:

    def __init__(self,ain1=12,ain2=13,ena=6,bin1=20,bin2=21,enb=26):
        self.AIN1 = ain1; self.AIN2 = ain2; 
        self.BIN1 = bin1; self.BIN2 = bin2; 
        self.PA  = 50 ; self.PB  = 50

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

    def setMotor(self, left, right):
        self.setGPIO_PWN( self.AIN1, self.AIN2, self.PWMA, right )
        self.setGPIO_PWN( self.BIN1, self.BIN2, self.PWMB, left )
    pass

    def setGPIO_PWN( self, ain1, ain2, pwma, value ) : 
        value = 100 if value > 100 else value 
        value = -100 if value < -100 else value 

        if value > 0 :
            GPIO.output(ain1,GPIO.HIGH)
            GPIO.output(ain2,GPIO.LOW)
            pwma.ChangeDutyCycle(value)
        elif value < 0 :
            GPIO.output(ain1,GPIO.LOW)
            GPIO.output(ain2,GPIO.HIGH)
            pwma.ChangeDutyCycle( - value)
        else :
            pwma.ChangeDutyCycle( 0 )
            GPIO.output(ain1,GPIO.LOW)
            GPIO.output(ain2,GPIO.LOW)
        pass 
    pass

    def forward(self, value=50):
        print("foward")
        self.setMotor( value, value)
    pass

    def backward(self, value=50):
        print("backward")
        self.setMotor( -value, -value)
    pass

    def stop(self):
        print("stop")
        self.setMotor( 0, 0 )
    pass

    def left(self):
        print("left")
        self.setMotor( 30, -30 )
    pass

    def right(self):
        print("right")
        self.setMotor( -30, 30 )
    pass

pass

if __name__=='__main__':
    GPIO.setwarnings(False)
    
    motor = Motor()

    try:
        duration = 3
        for i in range( 4 ) : 
            d = i%4
            if d == 0 : 
                motor.forward()
            elif d == 1 :
                motor.backward()
            elif d == 2 :
                motor.left()
            elif d == 3 :
                motor.right()
            pass

            time.sleep(duration) 
        pass
    except KeyboardInterrupt:
        print( "" )
    pass

    motor.stop()
    time.sleep(0.5)
    GPIO.cleanup()

    print( "Good bye!" )
pass
