# coding: utf-8
from time import sleep
import RPi.GPIO as GPIO
# Use "GPIO" pin numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Set LED pin as output
led_pin=17
GPIO.setup( led_pin, GPIO.OUT) 
while True:
   # Turn LED on
   GPIO.output(led_pin, GPIO.HIGH)
   sleep(1)
    # Turn LED off
   GPIO.output(led_pin, GPIO.LOW)
   sleep(1)
   print( "Running now .... " )
pass
