# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal, inspect
import numpy as np
from random import random
from time import sleep, time
from gpiozero import Buzzer
from TRSensor import TRSensor

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
    ) 

class LineTracker :

    def __init__(self, robot, signal_range=[240, 540], buzzer=None, max_run_time=0, debug=0 ):
        self.debug = debug
        self.robot = robot
        self.signal_range = signal_range
        self.max_run_time = max_run_time

        self.buzzer = buzzer if buzzer else Buzzer(4)

        self._running = 0  
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

        if 1 :
            self.thread = threading.Thread(name='self.pulse_checker', target=self.robot_move )
            self.thread.start()
        return
    pass 

    def stop( self ) :
        log.info(inspect.currentframe().f_code.co_name)

        self._running = 0 

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

        debug = self.debug

        self._running = 1 

        robot = self.robot 
        buzzer = self.buzzer

        # 시작음
        buzzer.beep(on_time=0.5, off_time=0.2, n = 2, background=True)

        # 라인 센서
        tr = TRSensor(signal_range=self.signal_range, debug=self.debug)

        interval = 0.01
        
        turn_speed = 15

        move_start = time()

        max_run_time = self.max_run_time

        while self._running and ( not max_run_time or time() - move_start < max_run_time ) :
            start = time()
            
            pos, norm, check_time = tr.read_sensor()

            if abs( pos ) < 1.2 :
                debug and log.info( "ROBOT forward")
                robot.forward()
            elif pos < 0 :
                debug and log.info( "ROBOT left")
                robot.left( turn_speed )
            elif pos > 0 :
                debug and log.info( "ROBOT right")
                robot.right( turn_speed )
            pass

            now = time()
            elapsed = now - start
            remaining_time = interval - elapsed
            
            if remaining_time > 0 :
                sleep( remaining_time )
            pass
        pass

        robot.stop()

        buzzer.beep(on_time=0.7, off_time=0.05, n = 3, background=True)

        self._running = 0
        self.thread = None

        if max_run_time :
            print( "Enter to quit." )
        pass
    pass 

pass

if __name__ == '__main__':
    print( "Hello..." ) 

    GPIO.setwarnings(False)

    from Motor import Motor 

    robot = Motor()
    
    lineTracker = LineTracker( robot=robot, max_run_time=40, debug=1 )

    lineTracker.start()

    def exit( result ) :
        lineTracker.stop()
        sleep( 0.5 ) 

        print( "Good bye!")

        import sys
        sys.exit( 0 )
    pass

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        print('You have pressed Ctrl-C.')

        exit( 0 )
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    input( "Enter to quit......" ) 

    exit( 0 )
    
pass
