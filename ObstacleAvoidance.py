import RPi.GPIO as GPIO
from time import sleep

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

from AlphaBot2 import AlphaBot2

Ab = AlphaBot2()

DR = 16
DL = 19

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DR,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(DL,GPIO.IN,GPIO.PUD_UP)

try:
    idx = 0 
    while True:
        idx += 1

        DL_status = GPIO.input(DL)
        DR_status = GPIO.input(DR)        
        
        if DL_status == 0 or DR_status == 0 :
            print( f"DL = {DL_status}, DR = {DR_status}" )

            Ab.left()          
        else:
            Ab.forward() 
            sleep(0.01)
            Ab.stop()
            sleep( 0.02 )
        pass
    pass  
except KeyboardInterrupt:
    GPIO.cleanup();
pass

