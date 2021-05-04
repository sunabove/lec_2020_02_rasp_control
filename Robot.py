#coding: utf-8

import sys, cv2, numpy as np, threading, logging as log, inspect, signal
import RPi.GPIO as GPIO    

from time import  sleep
from gpiozero import Buzzer
from Motor import Motor
from RGB_LED import RGB_LED
from Camera import Camera, generate_frame
from Servo import Servo
from IRRemote import IRRemote
from rpi_ws281x import Color
from JoyStick import JoyStick
import Functions as funtions

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
        self.camera     = Camera( motor = self.motor )
        self.servo      = Servo()
        self.joyStick   = JoyStick( self.servo )
        #self.irremote   = IRRemote( robot, buzzer=self.buzzer )

        # 시동 소리 내기
        self.rgb_led.light_effect( "flash", Color(0, 255, 0), duration=3 )         
        self.buzzer.beep(on_time=0.2, off_time=0.2, n = 2)

        # joystick service start
        threading.Thread(target=self.joyStick.service).start()
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        log.info(inspect.currentframe().f_code.co_name) 
        
        self.buzzer.close()
        log.info( "buzzer finished" ) 

        self.motor.finish()
        log.info( "motor finished" ) 

        self.rgb_led.finish() 
        log.info( "rgg_led finished" ) 

        self.camera.finish()
        log.info( "camera finished" ) 

        self.servo.finish()
        log.info( "servo finished" ) 

        if hasattr( self, "irremote" ) : 
            self.irremote.finish()
            log.info( "irremote finished" ) 
        pass

        self.joyStick.finish()
        log.info( "joyStick finished" )
    pass

    def stop(self) :
        self.stop_robot()
    pass

    def stop_robot(self) :
        log.info(inspect.currentframe().f_code.co_name) 

        self.motor.stop_motor()
        self.rgb_led.turn_off() # RGB LED 꺼기
    pass

    def speed_up( self, dv = 5 ) : # 속도 증가
        self.motor.speed_up( dv )
    pass

    def speed_down( self, dv = 5) : # 속도 감소 
        self.motor.speed_down( dv )
    pass

    def forward(self, speed = 30) :
        # 전진
        # 전진 경고음
        self.buzzer.beep(on_time=0.5, off_time=0.5, n = 1)
        # 전진 라이트 
        self.rgb_led.light_effect( "breath", Color(0, 255, 0) )
        
        self.motor.forward( speed )
    pass

    def backward(self, speed = 30) :
        # 후진 
        # 후진시 경고음 
        self.buzzer.beep(on_time=0.05, off_time=0.05, n = 3)
        # 후진시에는 빨간색으로 깜박인다.
        self.rgb_led.light_effect( "flash", Color(255, 0, 0) ) 

        self.motor.backward( speed )
    pass

    def left(self) : # 좌회전
        # 경고음 
        self.buzzer.beep(on_time=0.1, off_time=0.1, n = 2)

        self.motor.left()
        # LED 깜빡이기
    pass

    def right(self): # 우회전 
        # 경고음 
        self.buzzer.beep(on_time=0.1, off_time=0.1, n = 2)

        self.motor.right()
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

    def servo_stop( self ) : 
        self.servo.stop()
    pass

    def stop_servo( self ) : 
        self.servo.stop()
    pass

pass # -- Robot

app = None 
robot = None 

def stop():
    print( "", flush=True) 

    log.info( 'You have pressed Ctrl-C.' ) 
    
    robot.finish()

    app.do_teardown_appcontext()

    GPIO.setmode(GPIO.BCM)  

    log.info( "Good bye!" )
pass # -- stop

def service() : 
    log.info( "Hello....." )

    # web by flask framewwork
    from flask import Flask, render_template, Response, request, jsonify

    GPIO.setwarnings(False)

    global app 
    global robot 

    app = Flask(__name__, static_url_path='', static_folder='html/static', template_folder='html/templates')
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    
    robot = Robot()
    robot.camera.start_recording()    

    @app.before_request
    def before_request_func():
        pass
    pass

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
    def process_cmd():
        cmd = request.form.get("cmd")
        speed = request.form.get("speed")

        if speed :
            speed = int( speed )
        else :
            speed = 50 
        pass

        log.info(f"cmd={cmd}, speed={speed}")

        if cmd == "stop":
            robot.stop_robot()
            robot.stop_servo()
        elif cmd == "forward":
            robot.forward( speed )
        elif cmd == "backward":
            robot.backward( speed )
        elif cmd == "turnleft":
            robot.left()
        elif code == "turnright":
            robot.right()
        elif cmd == "servo_left":
            robot.servo_left()
        elif cmd == "servo_right":
            robot.servo_right()
        elif cmd == "servo_up":
            robot.servo_up()
        elif cmd == "servo_down":
            robot.servo_down()
        elif cmd == "servo_stop":
            robot.servo_stop()
        elif cmd == "shutdown" :
            funtions.shutdown()
        pass

        return "OK"
    pass

    log.info( "## Normal WEB")

    app.run(host='0.0.0.0', port=80, debug=False, threaded=True) 

    log.info( "Good bye!")
pass # -- service

if __name__=='__main__':    
    def signal_handler(signal, frame): 
        stop() 

        sleep( 2 )

        sys.exit(0)
    pass

    signal.signal(signal.SIGINT, signal_handler)
    
    GPIO.setwarnings(False)
    GPIO.cleanup()
    service()
pass