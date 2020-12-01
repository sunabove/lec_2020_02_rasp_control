#coding: utf-8

from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(4)
print( "buzzer start")
buzzer.beep(on_time=0.5, off_time=0.5, n = 4)
print( "buzzer end")

input("Enter to quit! ")
