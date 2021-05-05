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

def beep_warning( buzzer=None ) :
    if not buzzer : 
        buzzer = Buzzer(4)
    pass

    for frq in range( 4, 0, -1 ) : 
        t = 1/frq/3
        buzzer.beep(on_time=t, off_time=t, n = frq, background=False)
        sleep( 0.5 )
    pass
pass # -- beep_warning

def shutdown( buzzer = None ):
    print( '\nShutdown now ...' )
    beep_warning( buzzer )
    
    blink_internal_led( 0 )
    blink_internal_led( 1 )

    os.system( 'sync && sync && sudo poweroff' )
pass # -- shutdown

if __name__ == '__main__':
    beep_warning()
pass