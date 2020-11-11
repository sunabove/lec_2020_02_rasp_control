#coding: utf-8

from gpiozero import Buzzer
from time import sleep

bz = Buzzer(4)
bz.on()

sleep(5)