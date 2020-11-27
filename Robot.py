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

class Robot :
    def __init__(self): 
        super().__init__()

        self.motor = Motor()
        self.rgb_led = RGB_LED()
        self.camera = Camera()
        self.servo = Servo()  
    pass

    def stop(self) :
        self.motor.stop()
    pass

    def forward(self, speed = None) :
        self.motor.forward( speed )
    pass

    def backward(self, speed = None) :
        self.motor.backward( speed )
    pass

    def left(self) :
        self.motor.left()
    pass

    def right(self):
        self.motor.right()
    pass

    def stop_robot(self):
        self.servo.stop_servo()
        self.stop_motor()
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

        print(f"code={code}, speed={speed}")

        servo = robot.servo 

        if code == "stop":
            robot.stop()
            print("stop")
        elif code == "forward":
            robot.forward()
            print("forward")
        elif code == "backward":
            robot.backward()
            print("backward")
        elif code == "turnleft":
            robot.left()
            print("turnleft")
        elif code == "turnright":
            robot.right()
            print("turnright")
        elif code == "up":
            servo.VStep = -5
            print("up")
        elif code == "down":
            servo.VStep = 5
            print("down")
        elif code == "left":
            servo.HStep = 5
            print("left")
        elif code == "right":
            servo.HStep = -5
            print("right")
        pass

        return "OK"
    pass

    print( "## Normal WEB")
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True) 

pass