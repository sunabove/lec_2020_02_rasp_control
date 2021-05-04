# -*- coding: utf-8 -*-
from gpiozero import Button
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

def shutdown():
    print( '\nShutdown now ...' )
    blink_internal_led( 0 )
    blink_internal_led( 1 )

    os.system( 'sync && sync && sudo poweroff' )
pass