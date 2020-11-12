#coding: utf-8

from gpiozero import Buzzer
from time import sleep

bz = Buzzer(4)
bz.beep(on_time=0.5, off_time=0.5, n = 4)

input("Enter to quit! ")