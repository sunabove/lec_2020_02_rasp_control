# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal,  inspect
from gpiozero import Button
from random import random
from time import sleep, time

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class LineTracker : 

    JOY_STICK  = 7 # 조이스틱

    def __init__(self, robot, joystick = None):
        self.robot = robot

        self._running = False 

        self.then = time() 

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup( self.JOY_STICK, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect( self.JOY_STICK, GPIO.BOTH, callback=self.joystick_pressed)
    pass

    def __del__(self):
        self.finish()
    pass

    def joystick_pressed(self) :
        log.info(inspect.currentframe().f_code.co_name)
    pass

    def finish(self) :
        log.info(inspect.currentframe().f_code.co_name)

        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup( self.JOY_STICK )

        self.stop()
    pass

    def join(self) :
        pass
    pass

    def start(self):
        log.info(inspect.currentframe().f_code.co_name)

        self._running = True 

        if True :
            self.thread = threading.Thread(name='self.pulse_checker', target=self.robot_move )
            self.thread.start()
        return
    pass 

    def stop( self ) :
        log.info(inspect.currentframe().f_code.co_name)

        self._running = False 
    pass

    def is_running(self):
        return self._running
    pass  

    def robot_move (self) :
        log.info(inspect.currentframe().f_code.co_name)

        robot = self.robot

        now = time()
        interval = 0.04
        elapsed = now - self.then 
        if elapsed < interval :
            #log.info( f"sleep({interval - elapsed})" )
            sleep( interval - elapsed ) 
        pass 
    pass 

pass

if __name__ == '__main__':
    log.info( "Hello..." ) 

    GPIO.setwarnings(False)

    from Motor import Motor 

    robot = Motor()
    
    lineTracker = LineTracker( robot )

    lineTracker.start()

    def exit( result ) :
        lineTracker.stop()
        sleep( 0.5 ) 

        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup();
    pass

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        log.info('You have pressed Ctrl-C.')

        exit( 0 )

        import sys
        sys.exit( 0 )
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    input( "Enter to quit......" )

    exit( 0 )

    log.info( "Good bye!")
pass
