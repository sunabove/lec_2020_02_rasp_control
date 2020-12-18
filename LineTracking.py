# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal, inspect
import numpy as np
from random import random
from time import sleep, time
from TRSensor import TRSensor

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
    ) 

class LineTracker :

    def __init__(self, robot, white = 570, black=240 ):
        self.robot = robot
        self.white = white
        self.black = black 

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

        thread = self.thread
        if thread is not None :
            thread.join()
        pass
    pass

    def is_running(self):
        return self._running
    pass  

    def robot_move (self) :
        log.info(inspect.currentframe().f_code.co_name)

        self._running = True 

        robot = self.robot 

        tr = TRSensor(white=self.white, black=self.black)

        then = time()
        interval = 0.01
        elapsed = 0 
        idx = 0 

        prev_area = ""
        area_cnt = 0 
        turn_speed = 15

        while self._running : 
            now = time()
            elapsed = now - then 

            if elapsed < interval :
                sleep( interval - elapsed ) 
            else :
                pos, area, norm = tr.read_sensor()

                log.info( f"area_cnt={area_cnt}")

                if abs( pos ) < 0.1 :
                    log.info( "ROBOT forward")
                    robot.forward()
                elif pos < 0 :
                    log.info( "ROBOT right")
                    robot.right(turn_speed)
                elif pos > 0 :
                    log.info( "ROBOT left")
                    robot.left(turn_speed)
                pass

                if prev_area == area :
                    area_cnt += 1
                else : 
                    area_cnt = 0 
                    prev_area = area
                pass

                idx += 1
                then = now
            pass
        pass

        self.thread = None
    pass 

pass

if __name__ == '__main__':
    log.info( "Hello..." ) 

    GPIO.setwarnings(False)

    from Motor import Motor 

    robot = Motor()
    
    lineTracker = LineTracker( robot=robot )

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
