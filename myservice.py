# -*- coding: utf-8 -*-

from time import sleep
from threading import Thread

from robot import blink
from robot.oled import main
from robot import ShutDownBtn

targets = [ blink, main, ShutDownBtn ]

def start() : # start services
    for target in targets : 
        try : 
            Thread(target=target.service).start()
        except Exception as e:
            print( e )
        pass
    pass

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