# -*- coding:utf-8 -*-

from Common import check_pkg
for pkg in [ "shapely, libgeos-dev, shapely" ] :
        #"shapely, libgeos-dev, shapely"
        #"centerline, libgdal-dev, centerline" 
    	check_pkg( pkg )
pass

import RPi.GPIO as GPIO, threading, signal, inspect, sys, logging as log
import numpy as np, cv2 as cv
from math import cos, sin, atan2, pi
from random import random
from time import sleep, time, time_ns
from datetime import datetime
from LineTracker import LineTracker
from Common import get_polygon_intersection
from Config import cfg

log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO 
    ) 

class Image :
    def __init__(self, image, name, is_bin=False):
        self.image = image
        self.name = name
        self.is_bin = is_bin
pass # -- Image

class LineCamera( LineTracker ) :

    def __init__(self, robot, camera, buzzer=None, debug=0 ):
        super().__init__( robot=robot, buzzer=buzzer, debug = debug )

        self.camera = camera
        self.camera.lineCamera = self
        self.successive_time = 0
        self.move_idx = 0 
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

        # 환경 설정 데이터
        config = robot.config

        then = time()
        move = config[ "move"]

        if move :
            self.move_idx += 1
            if self.move_idx % 2 == 0 :
                #robot.stop()
                pass
            pass
        pass

        # 색깔 정의
        green = (0, 255, 0)
        blue  = (255, 0, 0)
        red = (0, 0, 255)
        yellow = (0, 255, 255)
        violet = (255, 0, 127)
        white = (255, 255, 255)
        black = (0, 0, 0)
        gray = (128, 128, 128)
        lightgray = light_gray = (211, 211, 211)
        sienna = (45, 82, 160)
        orange = (0, 69, 255)

        # 영상 처리 과정의 이미지들
        images = []

        overlay_name = config[ "overlay" ]

        # 목표 지점/차선 중심점
        cx = None
        cy = None
        theta = None # 방향 RADIAN
        angle = None # 방향 DEGREE
        inside_lane = False # 차선 내부 판별
        center_lane_width = 100 # 센터 라인 넓이

        # 원본 이미지
        image_org = image

        # 이미지 높이와 폭
        h_org, w_org = h, w = image.shape[:2]
        #h = len( image ); w = len( image[0] )
        total_area = w*h # 전체 면적

        # 회색조 변환 , 공식 grayscale = 0.114B + 0.587G + 0.299R
        # opencv image color order is in order Blue, Green and Red
        grayscale = 0.114*image[ :, :, 0 ] + 0.587*image[ :, :, 1 ] + 0.299*image[ :, :, 2 ]
        #gray =image[:,:,0]/3 + image[:,:,1]/3 + image[:,:,2]/3

        images.append( Image( grayscale, 'grayscale', False ))

        # 관심영역(ROI, Region Of Interest) 추출
        roi_ratio = 0.05
        rmh = int(h*roi_ratio)
        rmw = int(w*roi_ratio)
        roi = grayscale[ rmh : h - rmh, rmw : w - rmw ]

        # ROI 크기 축소
        scale_width = 160
        scale_factor = scale_width/roi.shape[1]
        scale_height = int( roi.shape[0]*scale_factor )
        scale = cv.resize( roi, (scale_width, scale_height) )

        # 필터를 이용한 노이즈 제거
        blur = scale
        #blur = cv.GaussianBlur(blur, (7, 7), 0)
        blur = cv.bilateralFilter(blur.astype(np.uint8), 7, 80, 80)
        
        images.append( Image( blur, 'blur', False ))
        
        # 이진화/임계치 적용
        threshold = config[ "threshold" ] # 65 110 #75 #50 #100
        thresh = np.where( blur < threshold, 1, 0)
        thresh = thresh.astype(np.uint8)

        images.append( Image( thresh, 'thresh', True ))

        remove_shade = False 
        if remove_shade : 
            # 형태학적 노이즈 제거
            thresh_open = thresh
            # 축소 / 이웃 보간법
            thresh_open = cv.resize(thresh_open, (thresh.shape[1]//10, thresh.shape[0]//10), cv.INTER_NEAREST) 
            # 확대
            thresh_open = cv.resize(thresh_open, thresh.shape[:2][::-1], cv.INTER_NEAREST) 
            thresh_open = np.where(thresh_open > 0, 1, 0 )

            images.append( Image( thresh_open, 'thresh_open', True ))

            # 임계치 영상에서 그림자 제거
            thresh_blur = thresh & thresh_open
            images.append( Image( thresh_blur, 'thresh_blur', True ))
        else :
            thresh_blur = thresh
        pass

        # 등고선 추출
        contours, hierarchy = cv.findContours(thresh_blur.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        overlay = None
        overlay_img_name = "original"
        overlay_idx = 0

        # 화면에 출력할 오버레이 이미지 검색
        if overlay_name and overlay_name not in [ "original", "successive" ] :
            self.successive_time = -1

            for idx, img in enumerate( images ) :
                if img.name == overlay_name :
                    overlay = 255*(1 - img.image) if img.is_bin else img.image
                    overlay_img_name = img.name
                    overlay_idx = idx + 1

                    break
                pass
            pass
        elif overlay_name == "successive" :
            if self.successive_time < 1 :
                self.successive_time = time()
            pass

            elapsed = int( time() - self.successive_time )//3
            idx = elapsed%len( images )
            img = images[ idx ]

            overlay = 255*(1 - img.image) if img.is_bin else img.image
            overlay_img_name = img.name
            overlay_idx = idx + 1
        pass # -- 화면에 출력할 오버레이 이미지 검색

        # ROI 영영 강조, ROI 영역 외부는 희미하게 처리
        image = image_org

        if overlay is not None :
            if overlay_img_name == "grayscale" :
                overlay = np.copy( grayscale[ rmh : h - rmh, rmw : w - rmw ] )
            pass

            image = grayscale
            image[ rmh : h - rmh, rmw : w - rmw ] = 0
            image *= 0.7

            if scale_factor != 1 :
                overlay = cv.resize(overlay.astype(np.uint8), roi.shape[:2][::-1] )
                image[ rmh : h - rmh, rmw : w - rmw ] = overlay
            else :
                image[ rmh : h - rmh, rmw : w - rmw ] = overlay
            pass

            # convert grayscale(1 channel) to rgb color(3 channel)
            grayscale_color = np.stack( [grayscale, grayscale, grayscale], axis=-1 )
            
            # draw roi area rectangle
            image = grayscale_color
        pass

        # ROI 영역 사각형 그리기
        cv.rectangle( image, (rmw, rmh), (w - rmw, h - rmh), color=(255, 255, 0), thickness=2)
        
        image = image.astype(np.uint8)

        image_draw = image[ rmh : h - rmh, rmw : w - rmw ]

        # 등고선 그리기
        
        polys = []
        max_poly = None
        max_poly_min_box = None
        max_area = 0
        min_area = total_area*scale_factor*0.005

        # 최대 면적 폴리곤(등고선) 검색
        sf = 1/scale_factor        
        for c in contours :
            area = cv.contourArea(c)
            
            if len(c) > 3 and area > min_area and area > max_area :
                max_area = area
                max_poly = c
            pass 

            polys.append( c )
        pass
        
        line_width = 2
        # 폴리곤 정점들의 최소 간격
        poly_epsilon = 18 #15 # 6 #20 # 12

        os = offset = (rmw, rmh) # 도형 그리기 오프셋

        for poly in polys :
            line_color = blue
            # 스케일 복원 
            poly[:,:] = poly[:,:]*sf            
            cv.drawContours(image, [poly], -1, blue, line_width +1, cv.LINE_AA, offset=offset)

            #poly_appr = cv.approxPolyDP(poly, poly_epsilon, True)
            #cv.drawContours(image_draw, [poly_appr], -1, blue, line_width, cv.LINE_AA)
        pass
        
        # 최대 폴리곤(= 차선) 그리기
        if max_poly is not None :
            # 폴리곤 단순화/최대 길이 적용
            useConvexHull = False
            if useConvexHull :
                # 폴리곤 외곽선 알고리즘 사용
                max_poly = cv.convexHull(max_poly, clockwise=True)
            else :
                # 폴리곤 단순화 알고리즘 사용
                max_poly = cv.approxPolyDP(max_poly, poly_epsilon, True)
            pass
            
            # 회전된 폴리곤 최소 사각형
            max_poly_min_box = cv.minAreaRect(max_poly)
            max_poly_min_box = cv.boxPoints(max_poly_min_box)
            max_poly_min_box = np.int0(max_poly_min_box)

            cv.drawContours(image, [max_poly_min_box], -1, violet, line_width + 2, cv.LINE_AA, offset=offset)
            cv.drawContours(image, [max_poly], -1, green, line_width, cv.LINE_AA, offset=offset)
        pass

        if max_poly is not None :
            # 차선 중심점 구하기
            # 이미지 모멘트
            M = cv.moments(max_poly) 

            if M["m00"] == 0 :
                M = cv.moments(max_poly_min_box)
            pass

            m00 = M["m00"]
            if m00 != 0 : 
                # 모멘트를 이용하여 검출 라인의 중심점 구하기 
                cx = M["m10"]/m00
                cy = M["m01"]/m00

                c = (int(cx + 0.5), int(cy + 0.5))

                u00 = m00
                u20 = M[ "mu20" ]/u00
                u02 = M[ "mu02" ]/u00
                u11 = M[ "mu11" ]/u00

                # 모멘트를 이용하여 검출 라인의 회전 각도 구하기
                theta = 0.5*atan2(2*u11, u20 - u02)
                angle = theta*180/pi

                # 차선 중심점 거리로 부터 중심점 내부 포함 여부 판별
                # 이 함수는 +1, -1 또는 0을 반환하여 점이 다각형 내부, 외부 또는 위에 있는지 여부를 나타냅니다.
                dist = cv.pointPolygonTest( max_poly, c, False )
                inside_lane = ( dist >= 0 )

                crosses = []
                r = max( w_org, h_org )
                a1 = [ cx, cy ]
                a2 = [ cx + 2*r*cos(theta), cy + 2*r*sin(theta) ]
                cross = get_polygon_intersection(a1, a2, max_poly)
                debug and print( "a1 = ", a1, ", a2 = ", a2, ", cross 1 = ", cross )

                if cross is not None :
                    cross = ( int(cross[0] + os[0] + 0.5), int(cross[1] + os[1] + 0.5) )
                    crosses.append( cross )
                pass

                a2 = [ cx + 2*r*cos(theta + pi), cy + 2*r*sin(theta + pi) ]
                cross = get_polygon_intersection(a1, a2, max_poly)
                debug and print( "a1 = ", a1, ", a2 = ", a2, ", cross 2 = ", cross )

                if cross is not None :
                    cross = ( int(cross[0] + os[0] + 0.5), int(cross[1] + os[1] + 0.5) )
                    crosses.append( cross ) 
                pass

                # 논리적 원점. 영상의 하단 가운데 점(마진 제외).
                origin = ( w_org//2, h_org - rmh ) 

                # 목표점 구하기 
                target_cross = None
                if True :
                    min_distum = 100_000_000
                    for cross in crosses :
                        dx = cross[0] - origin[0]
                        dy = cross[1] - origin[1]
                        distum = dx*dx + dy*dy
                        if distum < min_distum :
                            min_distum = distum
                            target_cross = cross
                        pass
                    pass
                pass

                useOrgAngle = False
                if useOrgAngle :
                    pass
                elif target_cross is not None :
                    t = [ cx + os[0], cy + os[1] ]
                    o = target_cross
                    #o = origin
                    theta = atan2(t[1] - o[1], - (t[0] - o[0]) )
                    angle = theta*180/pi
                    angle = abs(angle) - 90
                    #angle = (angle + 180)%360
                pass

                # 원점 그리기
                if True :
                    m = 6
                    rect_color = yellow
                    cross = origin
                    lt = ( cross[0] - m, cross[1] - m )
                    rb = ( cross[0] + m, cross[1] + m )
                    cv.rectangle( image, lt, rb, color=rect_color, thickness=2)
                pass

                # 가운데 가상의 센터 라인 그리기
                lw = center_lane_width
                m = 10
                center_lane = np.array( [ [ (w - lw)//2, rmh - m ], [ (w - lw)//2, h - rmh + m ], [ (w + lw)//2, h - rmh + m ], [ (w + lw)//2, rmh - m ] ])
                center_lane = center_lane.reshape((-1, 1, 2))
                    
                if True :
                    cv.drawContours(image, [center_lane], -1, lightgray, 1, cv.LINE_AA)
                pass

                # 라인의 두 끝점 그리기
                for cross in crosses :
                    m = 8
                    rect_color = yellow if cross == target_cross else orange
                    fill_color = red if cv.pointPolygonTest( center_lane, cross, False ) < 0 else green
                    
                    lt = ( cross[0] - m, cross[1] - m )
                    rb = ( cross[0] + m, cross[1] + m )

                    cv.rectangle( image, lt, rb, fill_color, -1 )
                    cv.rectangle( image, lt, rb, rect_color, thickness=2)
                pass

                # 무게 중심 십자가 그리기
                # 무게 중심 지점 원 그리기 / # 과제 : 중심점 내외부 여부에 따라서 색깔을 달리하도록 코딩한다.
                m = 14
                circle_color = yellow if inside_lane else red
                line_color = circle_color

                cv.line(image, (c[0] - m + os[0], c[1] + os[1]), (c[0] + m + os[0], c[1] + os[1]), line_color, 1)
                cv.line(image, (c[0] + os[0], c[1] - m + os[1]), (c[0] + os[0], c[1] + m + os[1]), line_color, 1)

                cv.circle(image, (c[0] + os[0], c[1] + os[1]), 4, circle_color)
                for radius in range( 6, m, 3 ) :
                    cv.circle(image, (c[0] + os[0], c[1] + os[1]), radius, circle_color)
                pass
                
            pass
        pass # -- 등고선 그리기

        if True : 
            # 영상 중심점 십자가 그리기
            m = 10
            cen_y, cen_x = image_draw.shape[:2]
            cen_y, cen_x = cen_y//2, cen_x//2

            line_color = white
            cv.rectangle(image_draw, (cen_x - m - 3, cen_y - 2), (cen_x + m + 3, cen_y + 2), line_color, -1)
            cv.rectangle(image_draw, (cen_x - 2, cen_y - m - 3), (cen_x + 2, cen_y + m + 3), line_color, -1)

            line_color = (255, 255, 0)
            cv.line(image_draw, (cen_x - m, cen_y), (cen_x + m, cen_y), line_color, 1 )
            cv.line(image_draw, (cen_x, cen_y -m), (cen_x, cen_y + m), line_color, 1 )

            # 하단 스케일바 그리기
            m = 1
            line_color = lightgray
            x = rmw
            y = h_org - rmh//2
            cv.rectangle(image, (x, y - m), (x + 200, y + m), line_color, -1 )

            for i in range(5) :
                m = 6 - 2*(i%2)
                cv.rectangle(image, (x - 1, y - m), (x + 1, y + m), line_color, -1 )
                x += 50
            pass

            camera.putTextLine( image, "200", 202, h_org - rmh//2 + 4, fg_color=gray )
        pass 

        # 영상에 표현할 텍스트 
        lines = []

        # 영상 크기 등의 텍스트 정보 추가 
        txt = f"LineCamera: W: {w_org}({scale.shape[1]}), H: {h_org}({scale.shape[0]}), Threshold: {threshold}, Overlay[{overlay_idx}]: {overlay_img_name}"

        lines.append( txt )

        # 라인 중심정 정보 텍스트 추가
        if cx is not None :
            cx = (cx + rmw) - w_org//2
            cy = h_org//2 - (cy + rmh)

            txt = f"CX: {cx:+3.0f}, CY: {cy:+3.0f}, ANGLE: {angle:+3.2f}, Inside: {inside_lane}"

            lines.append( txt )
        pass

        # 과제 : 영상 처리 시각(시:분:초, 초는 1/1000 초까지 표현) 텍스트 추가 
        txt = f"TIME CURRENT: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}"
        lines.append( txt )
        
        # 텍스트 이미지에 출력하기
        for txt in lines :
            camera.putTextLine( image, txt, tx, ty )
            ty += th
        pass

        # 로봇 이동
        if move :
            elapsed = time() - then

            log.info( f"line cam move: elapsed = {elapsed:.3f}" )

            # 모터 기준 속도
            base_speed = 8
            # 모터 최대 속도
            max_speed = 15

            if angle is None :
                angle = 45
            pass

            # 과제: 각도(angle)을 이용하여 모터 속도 조절값 계산하기
            control = -(max_speed - base_speed)*angle/90

            # 모터 속도
            left_speed  = base_speed - control
            right_speed = base_speed + control

            left_speed  = max( min( left_speed, max_speed ), -max_speed )
            right_speed = max( min( right_speed, max_speed ), -max_speed )

            robot.move( left_speed, right_speed )
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
