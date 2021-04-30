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

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for key in [ self.CTR, self.A, self.B, self.C, self.D ] : 
            GPIO.setup( key, GPIO.IN, GPIO.PUD_UP )
        pass
    pass

    def __del__(self) :
        GPIO.setmode(GPIO.BCM) 
        
        for key in [ self.CTR, self.A, self.B, self.C, self.D ] : 
            GPIO.cleanup( key )
        pass
    pass

    def control(self) :
        try:
            print( "JoyStick is ready to control." )
            
            target = self.target
            debug = self.debug

            while 1 :
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

                while key and GPIO.input(key) == 0:
                    sleep(0.01)
                pass
            pass
        except KeyboardInterrupt:
            pass
        pass
    pass # -- control

pass # -- JoyStick

def service() :
    servo = Servo()
    joyStick = JoyStick(target=servo)
    joyStick.control()
pass

def stop():
    pass
pass

if __name__ == '__main__':
    service()
pass