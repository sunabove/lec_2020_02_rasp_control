#coding: utf-8

import cv2, numpy as np, threading, logging, inspect 
import RPi.GPIO as GPIO    

from time import  sleep
from gpiozero import Buzzer
from Motor import Motor
from RGB_LED import RGB_LED
from Camera import Camera, generate_frame
from Servo import Servo
from IRRemote import IRRemote
from rpi_ws281x import Color

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class Robot :
    def __init__(self): 
        super().__init__()

        robot = self 

        self.buzzer     = Buzzer(4)   # 부저
        self.motor      = Motor()
        self.rgb_led    = RGB_LED()
        self.camera     = Camera()
        self.servo      = Servo()
        self.irremote   = IRRemote( robot )

        # 시동 소리 내기
        self.buzzer.beep(on_time=1, off_time=0.2, n = 1, background=False)
        self.buzzer.beep(on_time=0.2, off_time=0.2, n = 2)
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        log.info(inspect.currentframe().f_code.co_name) 

        self.buzzer.close()
        self.motor.finish()
        self.rgb_led.finish() 
        self.camera.finish()
        self.servo.finish()
        self.irremote.finish() 

        sleep( 0.5 )

        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
    pass

    def stop(self) :
        self.stop_robot()
    pass

    def stop_robot(self) :
        log.info(inspect.currentframe().f_code.co_name) 

        #elf.buzzer.beep(on_time=0.5, off_time=0.2, n = 1)

        self.motor.stop_motor()
        self.rgb_led.turn_off() # RGB LED 꺼기  
    pass

    def forward(self, speed = 30) :
        self.buzzer.beep(on_time=0.2, off_time=0.2, n = 4)
        
        self.motor.forward( speed )
        self.rgb_led.light_effect( "breath", Color(0, 255, 0) )
    pass

    def backward(self, speed = 30) :
        self.buzzer.beep(on_time=0.5, off_time=0.5, n = 4)

        self.motor.backward( speed )
        # 후진시에는 빨간색으로 깜박인다.
        self.rgb_led.light_effect( "flash", Color(255, 0, 0) ) 
    pass

    # 좌회전
    def left(self) :
        self.buzzer.beep(on_time=1, off_time=0.5, n = 2)

        self.motor.left()
        # LED 깜빡이기
    pass

    # 우회전 
    def right(self):
        self.buzzer.beep(on_time=1, off_time=0.5, n = 3)

        self.motor.right()
        # LED 깜빡이기
    pass

    def speed_up(self, speed = 10 ) :
        pass
    pass

    # servo control
    def servo_left( self ) : 
        self.servo.left()
    pass

    def servo_right( self ) : 
        self.servo.right()
    pass

    def servo_up( self ) : 
        self.servo.up()
    pass

    def servo_down( self ) : 
        self.servo.down()
    pass

pass

if __name__=='__main__':
    log.info( "Hello....." )

    # web by flask framewwork
    from flask import Flask, render_template, Response, request, jsonify

    app = Flask(__name__, static_url_path='', static_folder='html/static', template_folder='html/templates')
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    GPIO.setwarnings(False)
    
    robot = Robot()
    robot.camera.start_recording()    

    @app.before_request
    def before_request_func():
        log.info(inspect.currentframe().f_code.co_name) 

        global robot

        if robot is None :
            robot = Robot()
            robot.camera.start_recording()
        pass
    pass

    def handler(signal, frame):
        print()
        sleep( 0.01)

        log.info( 'You have pressed Ctrl-C.' ) 
        
        robot.finish()

        log.info( "Good bye!" )

        import sys
        sys.exit(0)
    pass

    import signal
    signal.signal(signal.SIGINT, handler)

    @app.route( '/' )
    @app.route( '/index.html' )
    @app.route( '/index.htm' )
    def index(): 
        return render_template('index_robot_server.html')
    pass 

    @app.route('/video_feed')
    def video_feed(): 
        return Response(generate_frame(robot.camera), mimetype='multipart/x-mixed-replace; boundary=frame')
    pass 

    @app.route("/cmd", methods=['POST'] )
    def cmd():
        code = request.form.get("cmd")
        speed = request.form.get("speed")

        if speed :
            speed = int( speed )
        else :
            speed = 50 
        pass

        print(f"code={code}, speed={speed}")

        if code == "stop":
            robot.stop_robot()
        elif code == "forward":
            robot.forward( speed )
        elif code == "backward":
            robot.backward( speed )
        elif code == "turnleft":
            robot.left()
        elif code == "turnright":
            robot.right()
        elif code == "left":
            robot.servo_left()
        elif code == "right":
            robot.servo_right()
        elif code == "up":
            robot.servo_up()
        elif code == "down":
            robot.servo_down()
        pass

        return "OK"
    pass

    log.info( "## Normal WEB")

    app.run(host='0.0.0.0', port=80, debug=False, threaded=True) 

    log.info( "Good bye!")

pass