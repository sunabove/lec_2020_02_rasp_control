#!/usr/bin/python
# -*- coding:utf-8 -*-
from AlphaBot import AlphaBot
from Servo import Servo
import threading
import socket #ip
import os

robot = AlphaBot()
pwm = Servo()
pwm.setPWMFreq(50)

#Set servo parameters
HPulse = 1500  #Sets the initial Pulse
HStep = 0      #Sets the initial step length
VPulse = 1500  #Sets the initial Pulse
VStep = 0      #Sets the initial step length
pwm.setServoPulse(1,VPulse)
pwm.setServoPulse(0,HPulse)

if __name__=='__main__': 
    
    # web by flask framewwork
    from flask import Flask, render_template, Response, request, jsonify
    app = Flask(__name__)
    
    from Camera import Camera

    camera = Camera()
    
    def gen(camera): 
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        pass
    pass

    @app.route('/video_feed')
    def video_feed(): 
        return Response(gen(camera), mimetype='multipart/x-mixed-replace; boundary=frame')
    pass 

    @app.route( '/' )
    @app.route( '/index.html' )
    @app.route( '/index.htm' )
    def index():
        return render_template("index.html")
    pass
        
    @app.route('/<filename>')
    def server_static(filename):
        return render_template(filename)
    pass

    @app.route('/fonts/<filename>')
    def server_fonts(filename):
        return render_template( f"fonts/{filename}" )
    pass
        
    @app.route("/cmd")
    def cmd():
        global HStep,VStep
        code = request.body.read().decode()
        speed = request.POST.get('speed')
        print(code)
        
        if(speed != None):
            robot.setPWMA(float(speed))
            robot.setPWMB(float(speed))
            print(speed)
        if code == "stop":
            HStep = 0
            VStep = 0
            robot.stop()
            print("stop")
        elif code == "forward":
            robot.forward()
            print("forward")
        elif code == "backward":
            robot.backward()
            print("backward")
        elif code == "turnleft":
            robotb.left()
            print("turnleft")
        elif code == "turnright":
            robot.right()
            print("turnright")
        elif code == "up":
            VStep = -5
            print("up")
        elif code == "down":
            VStep = 5
            print("down")
        elif code == "left":
            HStep = 5
            print("left")
        elif code == "right":
            HStep = -5
            print("right")
        pass

        return "OK"
    pass 

    print( "## Normal WEB")
    app.run(host='0.0.0.0', port=80, threaded=True) 
pass