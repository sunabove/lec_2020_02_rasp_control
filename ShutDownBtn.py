# -*- coding: utf-8 -*-
from gpiozero import Button
from subprocess import check_call
from time import sleep
import os

def internal_led(led_no, onoff):
    os.system( f'echo {onoff} | sudo dd status=none of=/sys/class/leds/led{led_no}/brightness' )
pass

def blink_internal_led( led_no=0 ) :
    for i in [1, 0]*5 :
        os.system( f'echo {i} | sudo dd status=none of=/sys/class/leds/led{led_no}/brightness' )
        sleep(1/4)
    pass
pass

def service() :
    blink_internal_led( 0 )
    blink_internal_led( 1 )

    internal_led( 1, 1 )

    def shutdown():
        print( '\nShutdown now ...' )
        blink_internal_led( 0 )
        blink_internal_led( 1 )

        check_call( 'sudo poweroff'.split() )
    pass

    shutdown_btn = Button(9, hold_time=3)
    shutdown_btn.when_held = shutdown

    input( "Enter Ctrl-C to quit" )

    while 1 :
        sleep( 10 )
    pass
pass

def stop() :
    print( 'Do nothing.' )
pass

if __name__ == '__main__':
    service()
pass