# -*- coding:utf-8 -*-
import threading, traceback, logging as log
from PCA9685 import PCA9685

class CameraServo:
 
    ROLL_MIN = 750
    ROLL_MID = 1750
    ROLL_MAX = 2750
    ROLL_DEG = (ROLL_MAX - ROLL_MIN) / 180.0
    
    PITCH_MIN = 1150
    PITCH_MID = 2100
    PITCH_MAX = 2800
    PITCH_DEG = ROLL_DEG

    def __init__(self, debug=0):
        log.basicConfig( format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
            )
        self.log = log.getLogger( self.__class__.__name__ )

        self.pwm = PCA9685(0x40, debug)
        self.pwm.setPWMFreq(50)
    
        self.set_position(0, self.ROLL_MID, self.ROLL_MIN, self.ROLL_MAX)
        self.set_position(1, self.PITCH_MID, self.PITCH_MIN, self.PITCH_MAX)
    pass

    def roll_percent(self, percent):
        self.set_position_percent(0, percent, self.ROLL_MIN, self.ROLL_MAX)
    pass

    def pitch_percent(self, percent):
        self.set_position_percent(1, percent, self.PITCH_MIN, self.PITCH_MAX)
    pass

    def set_position(self, servo, position, position_min, position_max):
        original = position
        
        position = min( position, position_max )
        position = max( position, position_min ) 
        
        self.log.debug(str(original) + " -> " + str(position))

        self.pwm.setServoPulse(servo, position)
        threading.Timer(0.01, self.stop).start()
    pass

    def set_position_percent(self, servo, percent, position_min, position_max):
        percent = min( percent, 100 )
        percent = max( percent, 0 )
        
        position = position_min + int((100.0 - percent) * (position_max - position_min) / 100.0)
        
        self.log.debug(str(percent) + "% -> " + str(position))
        self.set_position(servo, position, position_min, position_max)
    pass

    def set_position_degrees(self, servo, degrees, mid, position_min, position_max, points_per_degree):
        position = int(degrees * points_per_degree + mid)
        self.log.debug(str(degrees) + "deg -> " + str(position))
        self.set_position(servo, position, position_min, position_max)
    pass

    def stop(self):
        self.log.debug("Stopping")
        self.pwm.stop(0)
        self.pwm.stop(1)
    pass

pass

if __name__ == '__main__':

    try : 
        cameraServo = CameraServo()

        #cameraServo.roll_percent( 1 )
        cameraServo.pitch_percent( 1 )
    finally :
        pass
        #cameraServo.stop()
    pass

pass
