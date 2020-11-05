# coding: utf-8
from gpiozero import *
from time import sleep

led = LED(17)
button = Button(2)

button.when_pressed = led.on
button.when_released = led.off

input("Press the <ENTER> key to continue...")
