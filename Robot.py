#coding: utf-8

import cv2
import numpy as np 
import threading
from time import  sleep

import RPi.GPIO as GPIO    
from Camera import Camera, generate_frame
from Motor import Motor
from Servo import Servo

class Robot( Motor ):
    def __init__(self): 
        super().__init__()

        self.camera = Camera()
        self.servo = Servo()  
    pass

    def stop(self):
        self.motor_stop()
        self.servo.stop()
    pass
pass


if __name__=='__main__':
    GPIO.setwarnings(False)

    # web by flask framewwork
    from flask import Flask, render_template, Response, request, jsonify

    app = Flask(__name__, static_url_path='', static_folder='html/static', template_folder='html/templates')
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    robot = Robot()

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
        speed = request.form.get("spped")
        print(code)

        servo = robot.servo 
        
        if(speed != None):
            robot.setPWMA(float(speed))
            robot.setPWMB(float(speed))
            print(speed)
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