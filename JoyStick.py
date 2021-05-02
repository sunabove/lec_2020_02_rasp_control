import RPi.GPIO as GPIO
from time import sleep
from Servo import Servo

class JoyStick : 

    CTR = 7
    A = 8
    B = 9
    C = 10
    D = 11

    def __init__(self, target, debug = 0 ) :
        self.debug = debug
        self.target = target
        self.running = 0 

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for key in [ self.CTR, self.A, self.B, self.C, self.D ] : 
            GPIO.setup( key, GPIO.IN, GPIO.PUD_UP )
        pass
    pass

    def __del__(self) :
        self.running = False

        self.finish()
    pass

    def control(self) :
        try:
            print( "JoyStick is ready to control." )
            
            target = self.target
            debug = self.debug
            self.finished = 0 
            self.running = 1

            while self.running :
                key = None 
                if GPIO.input(self.CTR) == 0:
                    debug and print("center")
                    key = self.CTR 
                    target.stop()
                elif GPIO.input(self.A) == 0:
                    debug and print("up")
                    key = self.A
                    target.forward()
                elif GPIO.input(self.B) == 0:
                    debug and print("right")
                    key = self.B
                    target.right()
                elif GPIO.input(self.C) == 0:
                    debug and print("left")
                    key = self.C
                    target.left()
                elif GPIO.input(self.D) == 0:
                    debug and print("down")
                    key = self.D
                    target.backward()
                pass

                while self.running and key and GPIO.input(key) == 0:
                    sleep(0.01)
                pass
            pass
        finally :
            self.finished = 0 
            self.running = 0 
        pass
    pass # -- control

    def service(self) :
        self.control()
    pass # -- servic

    def stop(self):
        self.finish()
    pass

    def finish(self):
        self.running = 0

        GPIO.setmode(GPIO.BCM) 
        
        for key in [ self.CTR, self.A, self.B, self.C, self.D ] : 
            GPIO.cleanup( key )
        pass
    pass

pass # -- JoyStick

def service(debug=0) :
    servo = Servo()
    joyStick = JoyStick(target=servo, debug=debug)
    joyStick.service()
pass

def stop():
    pass
pass

if __name__ == '__main__':
    service(debug=1)
pass