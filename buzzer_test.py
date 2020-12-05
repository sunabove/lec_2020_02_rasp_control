#coding: utf-8

from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(4)
print( "buzzer start")
for frq in range( 1, 6 + 1 ) : 
    t = 1/frq
    buzzer.beep(on_time=t, off_time=t/2, n = int(frq), background=False)
    sleep( 1 )
pass
print( "buzzer end")

input("Enter to quit! ")
