# -*- coding: utf-8 -*-
from gpiozero import Button, Buzzer
from time import sleep
import os

def internal_led(led_no, onoff):
    os.system( f'echo {onoff} | sudo dd status=none of=/sys/class/leds/led{led_no}/brightness' )
pass

def blink_internal_led(led_no=0) :
    for i in [1, 0]*5 :
        os.system( f'echo {i} | sudo dd status=none of=/sys/class/leds/led{led_no}/brightness' )
        sleep(1/4)
    pass
pass

def beep_warning() :
    buzzer = Buzzer(4)

    cnt = 9 
    for frq in range( 1, cnt ) : 
        frq = cnt - frq
        t = 1/frq
        buzzer.beep(on_time=t, off_time=t/4, n = int(frq), background=False)
        sleep( 1 )
    pass

    buzzer.beep(on_time=5, off_time=1, n = 1, background=False)
    sleep( 1 )
pass # -- beep_warning

def shutdown():
    print( '\nShutdown now ...' )
    beep_warning()
    
    blink_internal_led( 0 )
    blink_internal_led( 1 )

    os.system( 'sync && sync && sudo poweroff' )
pass