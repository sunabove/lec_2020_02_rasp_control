#!/usr/bin/python3
# myservice.py
from time import sleep
from threading import Thread

import blink
from robot.oled import main

targets = [ blink, main ]

def start() :
    for target in targets : 
        Thread(target=target.service).start()
    pass

    while False :
        print( "Running ....") 
    sleep( 1 )
pass # -- start

def stop() :
    for target in targets : 
        target.stop()
    pass
pass # -- start

import signal
signal.signal( signal.SIGTERM, stop )   

if __name__ == '__main__':
    import sys

    argv = sys.argv

    if len( argv ) > 1 and argv[1] == 'stop' :
        stop()
    else :
        start()
    pass
pass