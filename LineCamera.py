# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal, inspect, sys, logging as log
import numpy as np, cv2
from math import cos, sin
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

        image_org = image

        # image height and width
        h, w = image.shape[:2]
        #h = len( image )
        #w = len( image[0] )

        # Convert to grayscale = 0.114B + 0.587G + 0.299R
        # opencv image color order is Blue Green Red
        gray = 0.114*image[ :, :, 0 ] + 0.587*image[ :, :, 1 ] + 0.299*image[ :, :, 2 ]
        #gray =image[:,:,0]/3 + image[:,:,1]/3 + image[:,:,2]/3

        # get ROI(Region Of Interest) image
        rm = roi_margin = min(h, w)*5//100
        roi = np.copy( gray[ rm : h - rm, rm : w - rm ] )

        # blur image to remove noise by using filter
        #kernel = np.ones((5, 5), np.float32)/25
        #blur = cv2.filter2D(image, -1, kernel)
        #blur = cv2.bilateralFilter(image.astype(np.uint8), 5, 80, 80)
        blur = cv2.GaussianBlur(roi, (5, 5), 0)

        #threshhold
        threshold = 100
        thresh = np.where(blur > threshold, 255, 0).astype(np.uint8)

        contours = None
        lines = None

        useContour = True

        if useContour :
            contours, hierarchy = cv2.findContours(255-thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else :
            # edge
            edge = cv2.Canny(thresh, 0, 255, None, 7)
            # hough line
            lines = cv2.HoughLinesP(edge, 1, np.pi/180, 50, None, 10, 10)
        pass

        line_cnt = len(lines) if lines is not None else 0 
        0 and log.info( f"lines: count = { line_cnt}" )
    
        overlay = thresh

        # ROI 영영 강조, ROI 영역 외부는 희미하게 처리
        image = gray
        image[ rm : h - rm, rm : w - rm ] = 0
        image *= 0.7 
        image[ rm : h - rm, rm : w - rm ] = overlay

        # convert grayscale(1 channel) to rgb color(3 channel)
        gray_color = np.stack( [gray, gray, gray], axis=-1 )
        #gray_color
        '''
        gray_color = np.empty( [h, w, 3] )
        gray_color[ :, :, 0 ] = gray
        gray_color[ :, :, 1 ] = gray
        gray_color[ :, :, 2 ] = gray
        '''
        
        # draw roi area rectangle
        image = gray_color
        cv2.rectangle( image, (rm, rm), (w - rm, h - rm), color=(255, 0, 0), thickness=1)
        
        image = image.astype(np.uint8)

        image_draw = image[ rm : h - rm, rm : w - rm ]

        line_color = (0, 255, 0)
        line_width = 2
        if contours is not None :
            cv2.drawContours(image_draw, contours, -1, line_color, line_width, cv2.LINE_AA)
        pass

        # draw hough lines
        if lines is not None :
            for line in lines:
               l = line[0] 
               cv2.line(image_draw, (l[0], l[1]), (l[2], l[3]), line_color, line_width, cv2.LINE_AA)
            pass
        pass

        txt = f"Mode: LineTrack 2"
        
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
