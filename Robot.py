#coding: utf-8

import sys, cv2, numpy as np, threading, logging as log, inspect, signal
import RPi.GPIO as GPIO    

from time import time, sleep
from gpiozero import Buzzer
from Motor import Motor
from RGB_LED import RGB_LED
from Camera import Camera, generate_frame
from Servo import Servo
from IRRemote import IRRemote
from rpi_ws281x import Color
from JoyStick import JoyStick
from ObstacleSensor import ObstacleSensor
from LineTrackerPID import LineTrackerPID
import Functions as funtions

log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class Robot :
    def __init__(self): 
        super().__init__()

        self.service = None
        self.beep_time = [0]*4 # 전후좌우

        self.buzzer     = Buzzer(4)   # 부저
        self.motor      = Motor()
        self.rgb_led    = RGB_LED()
        self.camera     = Camera( motor = self.motor )
        self.servo      = Servo()
        self.joyStick   = JoyStick( self.servo )
        self.irremote   = IRRemote( self, buzzer=self.buzzer )

        # 시동 소리 내기
        self.rgb_led.light_effect( "flash", Color(0, 255, 0), duration=3 )         
        self.buzzer.beep(on_time=0.1, off_time=0.1, n = 4)

        # joystick service start
        threading.Thread(target=self.joyStick.service).start()
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        log.info(inspect.currentframe().f_code.co_name) 

        self.stop_service()
        
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

        self.irremote.finish()
        log.info( "irremote finished" ) 

        self.joyStick.finish()
        log.info( "joyStick finished" )
    pass

    def stop_service(self) :
        service = self.service 
        self.service = None

        if service :
            service.stop()
        pass
    pass # -- stop_service

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

    def forward(self, speed = None) :
        # 전진
        # 전진 경고음
        now = time()
        if now - self.beep_time[0] > 3 : # 최소 5초후에 소리를 낸다.
            self.beep_time[0] = now 
            self.buzzer.beep(on_time=0.5, off_time=0.5, n = 1)

            # 전진 라이트 
            self.rgb_led.light_effect( "breath", Color(0, 255, 0) )
        pass        
        
        self.motor.forward( speed )
    pass

    def move(self, left = None, right=None):
        self.motor.move( left, right )
    pass # -- move

    def backward(self, speed = None) :
        # 후진 
        # 후진시 경고음 
        now = time()
        if now - self.beep_time[1] > 3 : # 최수 3초후에 소리를 낻다.
            self.beep_time[1] = now
            self.buzzer.beep(on_time=0.05, off_time=0.05, n = 3)
            
            # 후진시에는 빨간색으로 깜박인다.
            self.rgb_led.light_effect( "flash", Color(255, 0, 0) ) 
        pass

        self.motor.backward( speed )
    pass

    def left(self, turn_speed=None) : # 좌회전
        # 경고음 
        now = time()
        if now - self.beep_time[2] > 3 : # 최수 3초후에 소리를 낻다.
            self.beep_time[2] = now 
            self.buzzer.beep(on_time=0.1, off_time=0.1, n = 2)
        pass

        self.motor.left(turn_speed)
        # LED 깜빡이기
    pass

    def right(self, turn_speed=None): # 우회전 
        # 경고음 
        now = time()
        if now - self.beep_time[3] > 3 : # 최수 3초후에 소리를 낻다.
            self.beep_time[3] = now
            self.buzzer.beep(on_time=0.1, off_time=0.1, n = 2)
        pass

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

    log.info( 'Robot stopping ...' ) 

    global robot

    if robot :    
        robot.finish()
    pass

    if app : 
        app.do_teardown_appcontext()
    pass

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

    app = Flask(__name__, static_url_path='', static_folder='html', template_folder='html')
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

        if cmd in ( "stop", "servo_stop" ):
            robot.stop_robot()
            robot.stop_servo()
            robot.stop_service()
        elif cmd == "forward":
            robot.forward( speed )
        elif cmd == "backward":
            robot.backward( speed )
        elif cmd == "turn_left":
            robot.left()
        elif cmd == "turn_right":
            robot.right()
        elif cmd == "servo_left":
            robot.servo_left()
        elif cmd == "servo_right":
            robot.servo_right()
        elif cmd == "servo_up":
            robot.servo_up()
        elif cmd == "servo_down":
            robot.servo_down()
        elif cmd == "shutdown" :
            funtions.shutdown(robot.buzzer)
        elif cmd == "obstacle_sensor" :
            robot.stop_service()
            robot.service = ObstacleSensor( robot )
            robot.service.start()
        elif cmd == "line_tracking" :
            robot.stop_service()
            robot.service = LineTrackerPID( robot, buzzer = robot.buzzer )
            robot.service.start()
        pass

        return "OK"
    pass

    log.info( "## Normal WEB")

    app.run(host='0.0.0.0', port=80, debug=False, threaded=True) 

    log.info( "Good bye!")
pass # -- service

if __name__=='__main__':
    if 'stop' in sys.argv :
        stop()
    else :
        GPIO.setwarnings(False)
        GPIO.cleanup()

        def signal_handler(signal, frame):
            print()
            print( 'You have pressed Ctrl-C.' ) 

            stop() 

            sleep( 2 )

            sys.exit(0)
        pass

        signal.signal(signal.SIGINT, signal_handler)

        service()
    pass
pass