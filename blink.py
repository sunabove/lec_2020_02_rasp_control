# blink.py
from gpiozero import LED
from time import sleep

led_blink = True 

def service() :
   led_blink = True 

   print( f"led_blink = {led_blink}" )

   led = LED(17)
   
   while led_blink :
      led_blink and led.on()
      led_blink and sleep(1)
      led_blink and led.off()
      led_blink and sleep(1)
   pass
pass # -- service

def stop() :
   led_blink = False 

   print( f"led_blink = {led_blink}" )

   sleep( 2 )
pass # -- stop

if __name__ == '__main__':
   service()
pass

