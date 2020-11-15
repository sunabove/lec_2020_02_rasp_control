#coding: utf-8

import cv2
import numpy as np 

from Camera import Camera, generate_frame

class Robot:
    def __init__(self):
        self.camera = Camera()
    pass
pass

if __name__=='__main__':

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

    print( "## Normal WEB")
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True) 

pass