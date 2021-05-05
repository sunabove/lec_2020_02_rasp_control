# coding: utf-8

import RPi.GPIO as GPIO, threading, signal, inspect
from gpiozero import Button
from random import random
from time import sleep, time

from Motor import Motor 

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class ObstacleSensor : 

    LEFT_GPIO  = 19    # 왼   쪽 센서 GPIO 번호
    RIGHT_GPIO = 16    # 오른 쪽 센서 GPIO 번호

    def __init__(self, robot):
        self.robot = robot

        self.event_no = 0 
        self.turn_count = 0
        self.prev_state = 0
        self.move_delay = 0.01
        self.move_delay = 0

        self._running = False 

        self.then = time() 
    pass # -- __init__

    def __del__(self):
        self.finish()
    pass

    def finish(self):
        log.info(inspect.currentframe().f_code.co_name)

        self.stop()
    pass # -- finish

    def join(self) :
        pass
    pass  # -- join

    def service(self) :
        self.start()
    pass # -- service

    def start(self):
        log.info(inspect.currentframe().f_code.co_name)

        self._running = True

        GPIO.setmode( GPIO.BCM )
        
        GPIO.setup( self.LEFT_GPIO, GPIO.IN, GPIO.PUD_UP ) 
        GPIO.setup( self.RIGHT_GPIO, GPIO.IN, GPIO.PUD_UP ) 

        GPIO.add_event_detect( self.LEFT_GPIO, GPIO.BOTH, callback=self.robot_move )
        GPIO.add_event_detect( self.RIGHT_GPIO, GPIO.BOTH, callback=self.robot_move )

        self.robot.forward()
    pass # -- start

    def stop(self) :
        log.info(inspect.currentframe().f_code.co_name)

        self._running = False

        GPIO.setmode(GPIO.BCM)

        GPIO.remove_event_detect( self.LEFT_GPIO )
        GPIO.remove_event_detect( self.RIGHT_GPIO )

        GPIO.cleanup( self.LEFT_GPIO )
        GPIO.cleanup( self.RIGHT_GPIO )
    pass # -- stop

    def is_running(self):
        return self._running
    pass # -- is_running

    def robot_move(self, pin) :
        log.info(inspect.currentframe().f_code.co_name)

        self.event_no += 1

        robot = self.robot

        left_obstacle = GPIO.input( self.LEFT_GPIO ) == 0 
        right_obstacle = GPIO.input( self.RIGHT_GPIO ) == 0 

        state = 2*left_obstacle + right_obstacle

        log.info( f"state={state}, prev={self.prev_state}, LEFT={left_obstacle:d}, RIGHT={right_obstacle:d}" )

        if state == self.prev_state :
            log.info( "state is not changed. do nothing!" )
        elif left_obstacle == 0 and right_obstacle == 0 :
            # 장애물이 없을 때
            robot.forward( 10 )
        else :
            # 장애물이 있을 때
            self.turn_count += 1

            robot.left()

            sleep( 0.2 )
        pass

        self.prev_state = state
    pass # -- robot_move

pass # -- ObstacleSensor

obstacleSensor = None 

def service( motor = None ):
    if not motor : 
        motor = Motor()
    pass
    
    obstacleSensor = ObstacleSensor( motor )

    obstacleSensor.start()
pass # -- service

def stop():
    if obstacleSensor : 
        obstacleSensor.stop() 
    pass
pass # -- stop

if __name__ == '__main__':
    log.info( "Hello..." )
    log.info( 'Obstacle Sensor Start ...' )

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        log.info('You have pressed Ctrl-C.')

        stop()

        import sys
        sys.exit( 0 )
    pass # -- signal_handler

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    GPIO.setwarnings(False)

    service()

    input( "Enter to quit......" )

    stop()

    log.info( "Good bye!")
pass

