# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal, inspect, sys, logging as log
import numpy as np
from random import random
from time import sleep, time, time_ns
from gpiozero import Buzzer
from LineSensor import LineSensor
from LineTracker import LineTracker
from Config import cfg

log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
    ) 

class LineCamera( LineTracker ) :

    def __init__(self, robot, signal_range=None, buzzer=None, max_run_time=0, debug=0 ):
        signal_range = signal_range if signal_range else cfg('signal_range', [240, 540])

        super().__init__( robot, signal_range, buzzer, max_run_time, debug )
        
        self.pid = cfg( 'pid', [6, 1, 4]) 
    pass

    def robot_move(self) :
        log.info(inspect.currentframe().f_code.co_name)

        debug = self.debug

        self._running = True 

        robot = self.robot 
        buzzer = self.buzzer

        # 시작음
        buzzer.beep(on_time=0.5, off_time=0.2, n = 2, background=False)

        # 라인 센서
        lineSensor = LineSensor(signal_range=self.signal_range, debug=self.debug)

        debug and print()

        interval = 0.001 # 0.01
        
        base_speed = 10
        max_speed = 20
        
        move_start = time()

        idx = 0
        max_run_time = self.max_run_time

        pid = self.pid

        kp = pid[0]       # 현재 에러 반영 계수
        ki = pid[1]*0.01   # 에러 누적 반영 계수
        kd = - pid[2]*0.0001    # 에러 변화 반영 계수

        last_error = None
        error_integral = 0.0
        error_derivative = 0.0

        errors = []
        dts = []
        errors_max = 50 # 100 # 5
        dt = 0.0 

        check_time = time()
        last_check_time = check_time

        while self._running and ( not max_run_time or check_time - move_start < max_run_time ) :
            pos, norm, sum_norm, sensor, check_time = lineSensor.read_sensor()  # 라인 센서 데이트 획득

            # 현재 에러
            error = 0 - pos
            dt = check_time - last_check_time
            
            if len( errors ) > errors_max : 
                errors.pop( 0 )
                dts.pop( 0 )
            pass

            errors.append( error )
            dts.append( dt )

            # 에러 누적량
            if last_error :
                if errors_max > 5 : 
                    error_integral = 0
                    error_prev = 0 
                    
                    for error, dt in zip( errors, dts ) :
                        error_integral += (error_prev + error)/2*dt
                        error_prev = error
                    pass
                else :
                    error_integral += (error + last_error)/2*dt
                pass

                # 에러 변화량
                error_derivative = (error - last_error )/dt
            pass

            # 현재 에러, 에러 누적량, 에러 변화량으로 부터 제어값 결정 
            control = kp*error + ki*error_integral + kd*error_derivative

            # 모터 속도
            left_speed  = base_speed - control
            right_speed = base_speed + control

            left_speed  = max( min( left_speed, max_speed ), -max_speed )
            right_speed = max( min( right_speed, max_speed ), -max_speed )

            if debug :
                print( f"[{idx:05}] kp = {kp}, ki = {ki}, kd = {kd}, dt = {dt:.6}" )
                print( f"[{idx:05}] P = {error:5.2f}, I = {error_integral:5.2f} D = {error_derivative:5.2f}, control = {control:5.2f}, left = {left_speed:5.2f}, right = {right_speed:5.2f}" )
            pass

            robot.move( left_speed, right_speed )
            
            last_error = error
            last_check_time = check_time

            if interval :
                elapsed = time() - check_time
                #remaining_time = interval - elapsed
                remaining_time = max( 0, ( interval if not dts else 2*interval - sum(dts)/len(dts) ) - elapsed )
                sleep( remaining_time )
            pass

            idx += 1
        pass

        robot.stop()

        lineSensor.finish()

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

    GPIO.setwarnings( 0 )
    GPIO.cleanup()

    from Motor import Motor 

    robot = Motor() 
    
    lineCamera = LineCamera( robot=robot, max_run_time=40, debug=1 )

    lineCamera.start()

    def exit( result ) :
        lineCamera.stop()
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
