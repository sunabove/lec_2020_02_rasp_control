# coding: utf-8

import RPi.GPIO as GPIO, threading, signal,  inspect
from gpiozero import Button
from random import random
from time import sleep, time

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class ObstacleSensor : 

    RIGHT_GPIO = 16   # 오른 쪽 센서 GPIO 번호
    LEFT_GPIO = 19    # 왼쪽 센서 GPIO 번호 

    def __init__(self, robot):
        self.robot = robot

        self.turn_count = 0
        self.then = time()
        self.min_duration = 0.1

        self.start()
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        self.left.close()
        self.right.close()
    pass

    def join(self) :
        self.finish()
    pass

    def start(self):
        log.info(inspect.currentframe().f_code.co_name)

        self.left = Button( self.RIGHT_GPIO )
        self.right = Button( self.LEFT_GPIO ) 

        self.left.when_pressed = self.left_pressed
        self.left.when_released = self.left_released

        self.right.when_pressed = self.right_pressed
        self.right.when_released = self.right_released

        self.robot.forward()
    pass

    def left_pressed(self) :
        log.info(inspect.currentframe().f_code.co_name)
        # 왼쪽 장애물이 있을 때,
        self.turn( "left" )
    pass
    
    def left_released(self) :
        log.info(inspect.currentframe().f_code.co_name)
        # 오른쪽 장애물이 사라졌을 때,

        self.forward()
    pass

    def right_pressed(self) :
        log.info(inspect.currentframe().f_code.co_name)
        # 오르쪽 장애물이 있을 때
        self.turn( "right" )
    pass

    def right_released(self) :
        log.info(inspect.currentframe().f_code.co_name)
        # 오르쪽 장애물이 사라졌을 때

        self.forward()
    pass

    def turn(self, direction) :
        log.info(inspect.currentframe().f_code.co_name)

        now = time()

        if now - self.then < self.min_duration :
            pass
        elif self.robot.mode not in ( "left", "right" ) :
            self.turn_count += 1

            robot.left()

            sleep( 0.1 )

            if self.turn_count % 5 == 0 : 
                sleep( 0.01 )
                sleep( 0.02*random() )
            pass

            self.then = time()
        pass
    pass

    def forward(self) : 
        log.info(inspect.currentframe().f_code.co_name)

        now = time()

        if now - self.then < self.min_duration :
            pass
        elif self.robot.mode is not "forward" : 
            self.robot.forward()

            self.then = time()
        pass
    pass

pass

if __name__ == '__main__':
    log.info( "Hello..." )
    log.info( 'IRremote Test Start ...' )

    GPIO.setwarnings(False)

    from Motor import Motor 

    robot = Motor()

    obstacleSensor = ObstacleSensor( robot )

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        log.info('You have pressed Ctrl-C.')

        obstacleSensor.finish()

        sleep( 0.5 ) 

        import sys
        sys.exit( 0 )
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    signal.pause()

    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup();

    log.info( "Good bye!")
pass

