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

    LEFT_GPIO  = 19    # 왼 쪽 센서 GPIO 번호 
    RIGHT_GPIO = 16    # 오른 쪽 센서 GPIO 번호    

    def __init__(self, robot):
        self.robot = robot

        self.event_no = 0 
        self.turn_count = 0
        self.prev_state = 0
        self.then = time()

        self.start()
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        log.info(inspect.currentframe().f_code.co_name)

        self.robot.stop()

        GPIO.setmode(GPIO.BCM)  # uses numbering outside circles
        GPIO.cleanup( self.LEFT_GPIO )
        GPIO.cleanup( self.RIGHT_GPIO )
    pass

    def join(self) :
        pass
    pass

    def start(self):
        log.info(inspect.currentframe().f_code.co_name)

        GPIO.setmode(GPIO.BCM)  # uses numbering outside circles
        
        GPIO.setup( self.LEFT_GPIO, GPIO.IN, GPIO.PUD_UP) 
        GPIO.setup( self.RIGHT_GPIO, GPIO.IN, GPIO.PUD_UP) 

        GPIO.add_event_detect( self.LEFT_GPIO, GPIO.BOTH, callback=self.event_detect)
        GPIO.add_event_detect( self.RIGHT_GPIO, GPIO.BOTH, callback=self.event_detect)

        self.robot.forward()
    pass

    def event_detect(self, pin):
        log.info(inspect.currentframe().f_code.co_name)

        self.event_no += 1

        log.info( f"event_no = {self.event_no}, pin = {pin}" )
        
        if True :
            self.thread = threading.Thread(name='self.pulse_checker', target=self.move)
            self.thread.start()
        return
    pass

    def right_released(self) :
        log.info(inspect.currentframe().f_code.co_name)
        # 오르쪽 장애물이 사라졌을 때
        now = time()
        if now - self.then < self.min_duration :
            pass
        else :
            then = now
            self.right_obstacle = 0

            self.move()
        pass
    pass

    def move(self) :
        log.info(inspect.currentframe().f_code.co_name)

        now = time()
        interval = 0.04
        elapsed = now - self.then 
        if elapsed < interval :
            #log.info( f"sleep({interval - elapsed})" )
            sleep( interval - elapsed )
            
            return 
        pass

        left_obstacle = GPIO.input( self.LEFT_GPIO ) == 0 
        right_obstacle = GPIO.input( self.RIGHT_GPIO ) == 0 

        state = 2*left_obstacle + right_obstacle

        log.info( f"state={state}, prev={self.prev_state}, LEFT={left_obstacle:d}, RIGHT={right_obstacle:d}" )

        if state == self.prev_state : 
            # do nothing
            sleep( 0.01 ) 
        else :
            self.then = now 

            if left_obstacle == 0 and right_obstacle == 0 :
                # 장애물이 없을 때
                #log.info( "forward")
                robot.forward( 10 )
            else :
                # 장애물이 있을 때
                self.turn_count += 1

                robot.left()

                if self.turn_count % 5 == 0 : 
                    sleep( 0.01 )
                    sleep( 0.02*random() )
                pass
            pass

            self.prev_state = state
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

    def exit( result ) :
        obstacleSensor.finish()
        sleep( 0.5 ) 

        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup();
    pass


    def signal_handler(signal, frame):
        print("", flush=True) 
        
        log.info('You have pressed Ctrl-C.')

        exit()

        import sys
        sys.exit( 0 )
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    input( "Enter to quit......" )

    exit( 0 )

    log.info( "Good bye!")
pass

