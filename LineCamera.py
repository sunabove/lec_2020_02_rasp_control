# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO, threading, signal, inspect, sys, logging as log
import numpy as np, cv2 as cv
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

    def robot_move_by_camera(self, image, tx=10, ty=30, th=20, success=True, debug=0) :
        debug and log.info(inspect.currentframe().f_code.co_name)

        robot = self.robot 
        buzzer = self.buzzer
        camera = self.camera

        config = robot.config

        txts = [] # texts to draw on the image

        image_org = image

        # image height and width
        h_org, w_org = h, w = image.shape[:2]
        #h = len( image ); w = len( image[0] )

        # 회색조 변환 , 공식 grayscale = 0.114B + 0.587G + 0.299R
        # opencv image color order is Blue Green Red
        gray = 0.114*image[ :, :, 0 ] + 0.587*image[ :, :, 1 ] + 0.299*image[ :, :, 2 ]
        #gray =image[:,:,0]/3 + image[:,:,1]/3 + image[:,:,2]/3

        # 관심영역(ROI, Region Of Interest) 추룰
        rm = roi_margin = min(h, w)*5//100
        roi = gray[ rm : h - rm, rm : w - rm ]

        scale_width = 160
        scale_factor = scale_width/roi.shape[1]
        scale_height = int( roi.shape[0]*scale_factor )
        scale = cv.resize( roi, (scale_width, scale_height))

        # 필터를 이용한 노이즈 제거
        blur = scale
        blur = cv.GaussianBlur(blur, (7, 7), 0)
        #blur = cv.bilateralFilter(blur.astype(np.uint8), 5, 80, 80)
        #blur = cv.Laplacian(blur, cv.CV_16S, ksize=5)
        #blur = cv.morphologyEx(blur, cv.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=1)
        #blur = cv.morphologyEx(blur, cv.MORPH_OPEN, np.ones((5, 5), np.uint8), iterations=1)
        #blur = cv.filter2D(roi, -1, np.ones((5, 5), np.float32)/25)
        #blur = cv.filter2D(blur, -1, np.ones((21, 21), np.float32)/(21*21))
        
        #threshhold
        threshold = config[ "threshold" ] # 65 110 #75 #50 #100
        thresh = np.where( blur < threshold, 1, 0)
        #thresh = np.where(blur > threshold, 255, 0) #110
        #thresh = cv.adaptiveThreshold(blur.astype(np.uint8),255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,2)
        #thresh = cv.filter2D(thresh, -1, np.ones((5, 5), np.float32)/25)
        #thresh = cv.adaptiveThreshold(blur.astype(np.uint8),255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 0)

        # 등고선 추출
        contours, hierarchy = cv.findContours(thresh.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        overlay = 255*(1 - thresh)
        #overlay = blur
        #overlay = thresh

        # ROI 영영 강조, ROI 영역 외부는 희미하게 처리
        image = gray
        image[ rm : h - rm, rm : w - rm ] = 0
        image *= 0.7 
        if scale_factor != 1 :
            overlay = cv.resize(overlay.astype(np.uint8), roi.shape[:2][::-1] )
            image[ rm : h - rm, rm : w - rm ] = overlay
        else :
            image[ rm : h - rm, rm : w - rm ] = overlay
        pass

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
        cv.rectangle( image, (rm, rm), (w - rm, h - rm), color=(255, 0, 0), thickness=1)
        
        image = image.astype(np.uint8)

        image_draw = image[ rm : h - rm, rm : w - rm ]

        # 등고선 그리기
        draw_contour = 1 
        if draw_contour and contours is not None :
            line_color = (0, 255, 0); line_width = 2
            sf = 1/scale_factor
            for c in contours : 
                c[:,:,0] = c[:,:,0]*sf
                c[:,:,1] = c[:,:,1]*sf
                cv.drawContours(image_draw, [c], -1, line_color, line_width, cv.LINE_AA)
            pass
        pass

        txt = f"LineCamera: W: {w_org}, H: {h_org}, Threshold: {threshold}"

        txts.append( txt )
        
        for t in txts :
            camera.putTextLine( image, t, tx, ty )
            ty += th
        pass

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
