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
    pass

    def __del__(self) :
        self.running = False

        self.finish()
    pass

    def service(self) :
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)        
        
        for key in [ self.CTR, self.A, self.B, self.C, self.D ] : 
            GPIO.setup( key, GPIO.IN, GPIO.PUD_UP )
        pass

        debug = self.debug
        
        target = self.target
        self.finished = 0 
        self.running = 1

        #GPIO.add_event_detect( self.CTR, GPIO.FALLING, callback=self.target_control )
        #GPIO.add_event_detect( self.A, GPIO.FALLING, callback=self.target_control )
        GPIO.add_event_detect( self.B, GPIO.FALLING, callback=self.target_control )
        GPIO.add_event_detect( self.C, GPIO.FALLING, callback=self.target_control )
        GPIO.add_event_detect( self.D, GPIO.FALLING, callback=self.target_control )

        try : 
            while self.running :
                key = None 

                if GPIO.input(self.CTR) == 0:
                    key = self.CTR 
                    self.target_control( key )
                elif GPIO.input(self.A) == 0:
                    key = self.A
                    self.target_control( key )
                pass

                while self.running and key and GPIO.input(key) == 0:
                    sleep(0.01)
                pass
            pass
        except :
            pass
        finally: 
            self.finished = 1 
            self.running = 0
        pass
    pass

    def target_control(self, channel) :
        print( f"channel: {channel}" )

        target = self.target 

        if channel == self.CTR :
            target.stop()
        elif channel == self.A :
            target.forward()
        elif channel == self.B :
            target.right()
        elif channel == self.C :
            target.left()
        elif channel == self.D :
            target.backward()
        pass
    pass ## -- target_control

    def stop(self):
        self.finish()
    pass

    def finish(self):
        self.running = 0

        GPIO.setmode(GPIO.BCM) 
        
        for key in [ self.CTR, self.A, self.B, self.C, self.D ] : 
            GPIO.cleanup( key )
        pass
    pass # -- finish

pass # -- JoyStick

joyStick = None 
def service(debug=0) :
    servo = Servo()
    joyStick = JoyStick(target=servo, debug=debug)
    joyStick.service()
pass

def stop():
    if joyStick :
        joyStick.finish()
    pass
pass

if __name__ == '__main__':
    print( "Use the joyStick to control servos." )

    service(debug=1)

    input( "Enter any key to quit." )
pass