#coding: utf-8

import cv2
import numpy as np 

class Camera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FPS, 15)
        self.video.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'X264'))
    pass
    
    def __del__(self):
        self.video.release()
    pass

    def get_image(self):
        global ads
        car = ads.car 
        gps = ads.gps

        success, img = self.video.read()

        if not success :
            h = 480
            w= 640
            # black blank image
            img = np.zeros(shape=[h, w, 3], dtype=np.uint8)
            pass 
        pass

        img = cv2.flip( img, 0 )
        h, w, _ = img.shape # image height, width 

        x = 10   # text x position
        y = 20   # text y position
        h = 20   # line height

        txt = "Hello"
        self.putTextLine( img, txt , x, y )

        return img
    pass

    def get_frame( self ) : 
        # get video frame

        img = self.get_image()
         
        _, jpg = cv2.imencode('.jpg', img) 
        
        return jpg.tobytes()
    pass

    # opencv 이미지에 텍스트를 그린다.
    def putTextLine(self, img, txt, x, y ) :
        # /usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf
        font = cv2.FONT_HERSHEY_SIMPLEX # font
        
        fs = 0.4  # font size(scale)
        ft = 1    # font thickness 

        bg_color = (255, 255, 255) # text background color
        fg_color = (255,   0,   0) # text foreground color

        cv2.putText(img, txt, (x, y), font, fs, bg_color, ft + 2, cv2.LINE_AA)
        cv2.putText(img, txt, (x, y), font, fs, fg_color, ft    , cv2.LINE_AA) 
    pass
pass

if __name__=='__main__':
    camera = Camera() 

    while(True):
        # Capture frame-by-frame
        image = camera.get_image()

        # Display the resulting frame
        cv2.imshow('frame', image )
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        pass
    pass

    cv2.destroyAllWindows()
pass