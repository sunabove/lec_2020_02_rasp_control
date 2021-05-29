# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal, inspect, sys, logging as log
import numpy as np, cv2
from random import random
from time import sleep, time, time_ns
from LineTracker import LineTracker
from Config import cfg

log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
    ) 

class LineCamera( LineTracker ) :

    def __init__(self, robot, camera, buzzer=None, debug=0 ):
        super().__init__( robot=robot, buzzer=buzzer, debug = debug )

        self.camera = camera
        self.camera.lineCamera = self
    pass

    def robot_move(self) :
        # do nothing
        pass
    pass

    def stop( self ) :
        self.camera.lineCamera = None

        super().stop()
    pass

    def robot_move_by_camera(self, image, tx = 10, ty = 30, th = 20, success=True, debug=0) :
        debug and log.info(inspect.currentframe().f_code.co_name)

        self._running = True 

        robot = self.robot 
        buzzer = self.buzzer
        camera = self.camera 

        # image height and width
        h = len( image )
        w = len( image[0] )

        # Convert to grayscale = 0.114B + 0.587G + 0.299R
        # opencv image color order is Blue Green Red
        target = image
        gcf = gray_conv_factor = [0.114, 0.587, 0.299]
        gray = gcf[0]*target[ :, :, 0 ] + gcf[1]*target[ :, :, 1 ] + gcf[2]*target[ :, :, 2 ]

        # get ROI(Region Of Interest) image
        target = gray
        rm = roi_margin = min(h, w)*5//100
        roi = target[ rm : h - rm, rm : w - rm ]*1
        
        # convert graycale to color
        target = gray
        target *= 0.2
        target[ rm : h - rm, rm : w - rm ] = roi
        
        target = gray
        image = target.astype(np.uint8)

        txt = f"Mode: LineTrack"
        
        camera.putTextLine( image, txt, tx, ty )

        self._running = False
        self.thread = None

        return image
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
