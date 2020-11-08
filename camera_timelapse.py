#coding: utf-8

from subprocess import check_call
check_call("mkdir -p output", shell=True)
check_call("rm -rf output/*", shell=True)

import time, picamera

with picamera.PiCamera() as camera:
    camera.resolution = (1240, 1024)
    camera.start_preview()
    try:
        for i, filename in enumerate(camera.capture_continuous('output/image{counter:02d}.jpg')):
            time.sleep(1)
            if i == 10:
                break
    finally:
        camera.stop_preview()

check_call("sudo apt install ffmpeg -y", shell=True)
check_call("avconv -r 1 -i output/image%02d.jpg -r 10 -vcodec libx264 -crf 10 -g 15 output/tl.mp4", shell=True)
