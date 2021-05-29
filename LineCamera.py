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

    def putTextLine(self, image, txt, x, y ) :
        # opencv 이미지에 텍스트를 그린다.
        font = cv2.FONT_HERSHEY_SIMPLEX
        fs = 0.4  # font size(scale)
        ft = 1    # font thickness 

        bg_color = (255, 255, 255) # text background color
        fg_color = (255,   0,   0) # text foreground color

        cv2.putText(image, txt, (x, y), font, fs, bg_color, ft + 2, cv2.LINE_AA)
        cv2.putText(image, txt, (x, y), font, fs, fg_color, ft    , cv2.LINE_AA) 
    pass

    def robot_move_by_camera(self, image, tx = 10, ty = 30, th = 20, success=True, debug=0) :
        debug and log.info(inspect.currentframe().f_code.co_name)

        self._running = True 

        robot = self.robot 
        buzzer = self.buzzer
        camera = self.camera 

        # get ROI(Region Of Interest) image

        h = len( image )
        w = len( image[0] )

        # Eyes are most sensitive to green light, less sensitive to red light, and the least sensitive to blue light.
        # Therefore, the three colors should have different weights in the distribution.
        # Grayscale  = 0.299R + 0.587G + 0.114B

        # opencv image order is BGR
        gray = 0.299*image[:,:,2] + 0.587*image[:,:,1] + 0.114*image[:,:,0]

        rm = roi_margin = min(h, w)*5//100

        roi = gray[ rm : h - rm, rm : w - rm ]

        target = gray

        image = target.astype(np.uint8)

        txt = f"Mode: LineTrack"
        
        self.putTextLine( image, txt, tx, ty )

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
