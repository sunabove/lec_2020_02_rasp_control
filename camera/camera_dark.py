# code: utf-8
import picamera
from time import sleep
from fractions import Fraction

with picamera.PiCamera() as camera:
    # Set a framerate of 1/6fps, then set shutter
    # speed to 6s and ISO to 800
    camera.framerate = Fraction(1, 6)
    camera.shutter_speed = 6000
    camera.exposure_mode = 'off'
    camera.iso = 400 #max 800
    # Give the camera a good long time to measure AWB
    # (you may wish to use fixed AWB instead)
    sleep(10)
    # Finally, capture an image with a 6s exposure. Due
    # to mode switching on the still port, this will take
    # longer than 6 seconds
    camera.capture('dark.jpg')
pass
