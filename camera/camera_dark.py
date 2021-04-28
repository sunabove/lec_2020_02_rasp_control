# code: utf-8
import picamera
from time import sleep
from fractions import Fraction

with picamera.PiCamera() as camera:
    camera.framerate = Fraction(1, 6)
    camera.shutter_speed = 200 #miliseconds
    camera.exposure_mode = 'off'
    camera.iso = 400 #max 800
    # Give the camera a good long time to measure AWB
    # (you may wish to use fixed AWB instead)
    sleep(1)
    # Finally, capture an image with a 6s exposure. Due
    # to mode switching on the still port, this will take
    # longer than 6 seconds
    camera.capture('dark.jpg')
pass
