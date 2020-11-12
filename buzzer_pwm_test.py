#coding: utf-8
from gpiozero import *
from time import sleep

bz = PWMLED(4)

for i in range( 0, 101, 10 ) :
    bz.value =  i/100
    sleep( 0.4 )
pass
