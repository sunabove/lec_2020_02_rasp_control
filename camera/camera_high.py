import os
import picamera

try:
    os.unlink('my_video.mp4')
    os.unlink('my_video.h264')
except: pass

with picamera.PiCamera() as camera:
    camera.hflip = True
    camera.vflip = True
    camera.resolution = (640, 480)
    camera.framerate = 90
    camera.start_recording('my_video.h264')
    camera.wait_recording(10)
    camera.stop_recording()
    
from subprocess import check_call
check_call("MP4Box -fps 30 -add my_video.h264 my_video.mp4", shell=True)
