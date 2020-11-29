# coding: utf-8

from time import sleep
from adafruit_servokit import ServoKit
from PCA9685  import PCA9685

kit = ServoKit(channels=16)

kit.continuous_servo[0].throttle = -0.01
#kit.continuous_servo[1].throttle = 0.6 

sleep( 0.02 )   

print( "init")

pwm = PCA9685()
pwm.setPWMFreq(50)

pwm.setPWM(0, 0, 0)
sleep(1)
pwm.setPWM(1, 0, 0)
sleep(1)

