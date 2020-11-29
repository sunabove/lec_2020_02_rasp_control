#coding: utf-8

import cv2
import numpy as np 
import threading
from time import  sleep

import RPi.GPIO as GPIO    
from Motor import Motor
from RGB_LED import RGB_LED
from Camera import Camera, generate_frame
from Servo import Servo 

from rpi_ws281x import Color

class Robot :
    def __init__(self): 
        super().__init__()

        self.motor      = Motor()
        self.rgb_led    = RGB_LED()
        self.camera     = Camera()
        self.servo      = Servo()
    pass

    def stop(self) :
        self.motor.stop()
        # LEF 끈다.
        self.rgb_led.turn_off()
    pass

    def forward(self, speed = 50) :
        self.motor.forward( speed )
        self.rgb_led.light_effect( "breath", Color(0, 255, 0) )
    pass

    def backward(self, speed = 50) :
        self.motor.backward( speed )
        # 후진시에는 빨간색으로 깜박인다.
        self.rgb_led.light_effect( "flash", Color(255, 0, 0) ) 
    pass

    # 좌회전
    def left(self) :
        self.motor.left()
        # LED 깜빡이기
    pass

    # 우회전 
    def right(self):
        self.motor.right()
        # LED 깜빡이기
    pass

    def stop_robot(self):
        self.stop_motor()
        self.servo.stop()
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
    GPIO.setwarnings(False)

    # web by flask framewwork
    from flask import Flask, render_template, Response, request, jsonify

    app = Flask(__name__, static_url_path='', static_folder='html/static', template_folder='html/templates')
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    robot = Robot()
    robot.camera.start_recording()

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
            robot.stop()
        elif code == "forward":
            robot.forward( speed )
        elif code == "backward":
            robot.backward( speed 
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

    print( "## Normal WEB")
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True) 

pass