# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal, inspect, sys
import numpy as np
from random import random
from time import sleep, time
from gpiozero import Buzzer
from TRSensor import TRSensor
from LineTracker import LineTracker

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
    ) 

class LineTrackerPID( LineTracker ) :

    def __init__(self, robot, signal_range=[240, 540], buzzer=None, pid=[-6, 0, 4], max_run_time=0, debug=0 ):
        super().__init__( robot, signal_range, buzzer, max_run_time, debug )
        
        self.pid = pid
    pass

    def robot_move (self ) :
        log.info(inspect.currentframe().f_code.co_name)

        debug = self.debug

        self._running = True 

        robot = self.robot 
        buzzer = self.buzzer

        # 시작음
        buzzer.beep(on_time=0.5, off_time=0.2, n = 2, background=False)

        # 라인 센서
        tr = TRSensor(signal_range=self.signal_range, debug=self.debug)

        debug and print()

        then = time()
        interval = 0.01
        
        base_speed = 10
        max_speed = 20
        min_speed = -20
        
        last_error = 0.0 
        errors = []
        errors_max = 80

        move_start = time() 
        start_prev = None

        pid = self.pid

        kp = pid[0]  # 현재 에러 반영 계수
        ki = pid[1]  # 에러 누적 반영 계수
        kd = pid[2]  # 에러 변화 반영 계수

        idx = 0
        max_run_time = self.max_run_time

        while self._running and ( not max_run_time or time() - move_start < max_run_time ) :
            start = time()
            
            pos, norm = tr.read_sensor()  # 라인 센서 데이트 획득

            # 현재 에러
            error = 0 - pos
            
            if len( errors ) > errors_max : 
                errors.pop( 0 )
            pass

            errors.append( error )

            # 에러 누적량
            error_integral = sum( errors ) if ki else 0
        
            # 에러 변화량
            error_derivative = error - last_error 

            # 현재 에러, 에러 누적량, 에러 변화량으로 부터 제어값 결정 
            control = kp*error + ki*error_integral + kd*error_derivative

            # 모터 속도
            left_speed = base_speed + control
            right_speed = base_speed - control

            left_speed = min( left_speed, max_speed )
            left_speed = max( left_speed, min_speed )

            right_speed = min( right_speed, max_speed )
            right_speed = max( right_speed, min_speed )

            if debug :
                print( f"[{idx:05}] kp = {kp}, ki = {ki}, kd = {kd}" )
                print( f"[{idx:05}] P = {error:5.2f}, I = {error_integral:5.2f} D = {error_derivative:5.2f}, control = {control:5.2f}, left = {left_speed:5.2f}, right = {right_speed:5.2f}" )
            pass

            robot.move( left_speed, right_speed )
            
            last_error = error

            start_prev = start
            now = time()
            elapsed = now - start
            remaining_time = interval - elapsed
            
            if remaining_time > 0 :
                sleep( remaining_time )
            pass

            idx += 1
        pass

        robot.stop()

        buzzer.beep(on_time=0.7, off_time=0.05, n = 3, background=True)

        log.info( f"Move stopped." )

        self._running = False
        self.thread = None

        if max_run_time :
            print( "Enter to quit." )
        pass
    pass  # -- robot_move

pass

if __name__ == '__main__':
    print( "Hello..." ) 

    GPIO.setwarnings(False)

    from Motor import Motor 

    robot = Motor()

    pid=[-6, 0, 4]

    argv = sys.argv[1:]

    if argv :
        pid =[0]*3
        if len( argv ) > 0 : pid[0] = float( argv[0] )
        if len( argv ) > 1 : pid[1] = float( argv[1] )
        if len( argv ) > 2 : pid[2] = float( argv[2] )
    pass
    
    lineTracker = LineTrackerPID( robot=robot, max_run_time=40, pid=pid, debug=1 )

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
