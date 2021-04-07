# -*- coding: utf-8 -*-
from gpiozero import Button
from subprocess import check_call

def shutdown():
    print( 'Shuddown now ...' )
    check_call( ['sudo', 'poweroff'] )
pass

shutdown_btn = Button(7, hold_time=5)
shutdown_btn.when_held = shutdown()

input( "Enter to quit" )