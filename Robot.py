#coding: utf-8

import cv2
import numpy as np 
from time import  sleep

from Camera import Camera, generate_frame
from Motor import Motor
from Servo import Servo

class Robot( Motor ):
    def __init__(self): 
        super().__init__()

        self.camera = Camera()
        self.servo = Servo() 

        self.thread = None

        self.servo_thread()
    pass

    def servo_thread( self ):
        if self.thread is None :
            import threading

            self.thread = threading.Thread(target=self.servo_thread, args=[] )
            self.thread.setDaemon(True)
            self.thread.start()

            return
        pass

        servo = self.servo

        while True : 
            if servo.HStep != 0 :
                servo.HPulse += servo.HStep
                if servo.HPulse >= 2500 : 
                    servo.HPulse = 2500
                elif servo.HPulse <= 500 :
                    servo.HPulse = 500
                pass
                #set channel 2, the Horizontal servo
                servo.setServoPulse(0,servo.HPulse)    
            pass

            if servo.VStep != 0 :
                servo.VPulse += servo.VStep
                if servo.VPulse >= 2500 : 
                    servo.VPulse = 2500
                elif servo.VPulse <= 500 :
                    servo.VPulse = 500
                pass
                #set channel 3, the vertical servo
                servo.setServoPulse(1,servo.VPulse)
            pass

            sleep( 0.02 )
        pass
    pass 
pass


if __name__=='__main__':
    import RPi.GPIO as GPIO
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
        global HStep,VStep
        code = request.form.get("cmd")
        speed = request.form.get("spped")
        print(code)

        servo = robot.servo 
        
        if(speed != None):
            robot.setPWMA(float(speed))
            robot.setPWMB(float(speed))
            print(speed)
        if code == "stop":
            servo.HStep = 0
            servo.VStep = 0
            
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