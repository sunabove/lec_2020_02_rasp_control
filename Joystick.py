import RPi.GPIO as GPIO
from time import sleep
from Motor import Motor

motor = Motor()

CTR = 7
A = 8
B = 9
C = 10
D = 11
BUZ = 4

def beep_on():
    GPIO.output(BUZ,GPIO.HIGH)
pass

def beep_off():
    GPIO.output(BUZ,GPIO.LOW)
pass

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUZ,GPIO.OUT)
for key in [ CTR, A, B, C, D ] : 
    GPIO.setup(key,GPIO.IN,GPIO.PUD_UP)
pass

try:
    print( "JoyStick is ready to control." )
    while 1 :
        key = None 
        if GPIO.input(CTR) == 0:
            print("center")
            key = CTR 
            beep_on();
            motor.stop();
        elif GPIO.input(A) == 0:
            print("up")
            key = A
            beep_on();
            motor.forward();            
        elif GPIO.input(B) == 0:
            print("right")
            key = B
            beep_on();
            motor.right();
        elif GPIO.input(C) == 0:
            print("left")
            key = C
            beep_on();
            motor.left();
        elif GPIO.input(D) == 0:
            print("down")
            key = D
            beep_on();
            motor.backward();
        else:
            beep_off();
        pass

        while key and GPIO.input(key) == 0:
            sleep(0.01)
        pass
    pass
except KeyboardInterrupt:
    GPIO.cleanup()
pass