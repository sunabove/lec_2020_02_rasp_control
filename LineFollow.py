# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal, inspect
import numpy as np
from random import random
from time import sleep, time
from TRSensor import TRSensor

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname) [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
    ) 

class LineTracker :

    def __init__(self, robot, joystick = None):
        self.robot = robot

        self._running = False  
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        log.info(inspect.currentframe().f_code.co_name)
        
        self.stop()
    pass

    def join(self) :
        pass
    pass

    def start(self):
        log.info(inspect.currentframe().f_code.co_name)

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

        self._running = True 

        robot = self.robot

        tr = TRSensor()

        then = time()
        interval = 0.04
        elapsed = 0 
        idx = 0 

        white = 600
        black = 300

        while self._running : 
            now = time()
            elapsed = now - then 

            if elapsed < interval :
                #log.info( f"sleep({interval - elapsed})" )
                sleep( interval - elapsed ) 
                continue
            pass
            
            sensors = tr.read_analog()

            if np.all( sensors > white ) :
                log.info( f"[{idx:04d}] [STOP] : All White {sensors}" )
            elif np.all( sensors < black ) :
                log.info( f"[{idx:04d}] [FORE] : All Black {sensors}" )
            else :
                log.info( f"[{idx:04d}] sensors={sensors}" )
            pass

            idx += 1

            then = now
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
