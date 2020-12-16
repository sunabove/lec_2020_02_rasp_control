#coding: utf-8

from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(4)

print( "buzzer start")

def beep_warning() :
    cnt = 9 
    for frq in range( 1, cnt ) : 
        frq = cnt - frq
        t = 1/frq
        buzzer.beep(on_time=t, off_time=t/4, n = int(frq), background=False)
        sleep( 1 )
    pass

    buzzer.beep(on_time=5, off_time=1, n = 1, background=False)
    sleep( 1 )
pass

beep_warning()

print( "buzzer end")

#input("Enter to quit! ")