# coding: utf-8
from gpiozero import LED
from time import sleep

led = LED(17)
while True:
    led.on()
    sleep(0.25)
    led.off()
    sleep(0.25)
    print( "Running now .... " )
pass
