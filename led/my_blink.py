# coding: utf-8
from time import sleep
import RPi.GPIO as GPIO
# Use "GPIO" pin numbering
GPIO.setmode(GPIO.BCM)
# Set LED pin as output
led_pin = 17
GPIO.setup(led_pin, GPIO.OUT) 
while True :
    print( "Running now ...." )
    # Turn LED on
    GPIO.output(led_pin, GPIO.HIGH)
    sleep(1)
    # Turn LED off
    GPIO.output(led_pin, GPIO.LOW)
    sleep(1)   
pass
