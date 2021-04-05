#!/usr/bin/python3
# myservice.py
from time import sleep
from threading import Thread

import blink
from robot.oled import main

targets = [ blink, main ]

def start() : # start services
    for target in targets : 
        try : 
            Thread(target=target.service).start()
        except Exception as e:
            print( e )
        pass
    pass

    while False :
        print( "Running ....") 
    sleep( 1 )
pass # -- start

def stop() : # stop services
    for target in targets : 
        try : 
            target.stop()
        except Exception as e :
            print( e )
        pass
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