# coding: utf-8

import signal, time, threading, inspect

from time import sleep
from rpi_ws281x import Adafruit_NeoPixel, Color

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class RGB_LED : 

    def __init__(self) : 
        # LED strip configuration:
        LED_COUNT      = 4       # Number of LED pixels.
        LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
        LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
        LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL    = 0

        # Create NeoPixel object with appropriate configuration.
        # Intialize the library (must be called once before other functions).
        # run as root 
    
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

        self.strip.begin()
        self.strip.show()

        self.rgb = 0
        self.light_type = None
        self.is_off = False
        self.duration_to = None 

        self._running = False

        self._thread = threading.Thread(target = self._lightLoop)
        self._thread.setDaemon(True)
        self._thread.start()
    pass

    def __del__(self):
        self.finish()
    pass

    def finish( self ) :
        self.turn_off()
        self._running = False

        _thread = self._thread
        if _thread :
            _thread.join()
        pass        
    pass

    def join(self) :
        _thread = self._thread 
        if _thread is not None :
            _thread.join()
        pass
    pass

    def begin(self):
        self.strip.begin()
    pass

    def show(self):
        self.strip.show()
    pass

    def setPixelColor(self, led_no, rgb):
        self.strip.setPixelColor(led_no, rgb)
    pass

    def light_effect(self, light_type="", rgb=Color(0,0,0), duration=None):
        log.info(inspect.currentframe().f_code.co_name) 
        log.info( f"light_type: {light_type}" )

        self.light_type = light_type
        self.rgb = rgb
        if duration is None :
            self.duration_to = None 
        else :
            self.duration_to = time.time() + duration
        pass
    pass 

    def turn_off(self):
        self.light_type = None
        self.rgb = Color(0,0,0)
    pass 

    def _lightLoop(self):
        log.info(inspect.currentframe().f_code.co_name) 

        self._running = True 

        flashTime = [0.3, 0.2, 0.1, 0.05, 0.05, 0.1, 0.2, 0.5, 0.2]
        flashTimeIndex = 0 
        f = lambda x: (-1/10000.0)*x*x + (1/50.0)*x 
        x = 0

        strip = self.strip 
        numPixels = strip.numPixels()
        
        while self._running :
            duration_to = self.duration_to
            if duration_to is not None :
                # 일정 시간이 지나면, LED를 끈다.
                now = time.time()
                if now > duration_to :
                    self.turn_off()
                pass
            pass

            light_type = self.light_type
            rgb = self.rgb 

            if light_type is None :
                if not self.is_off :
                    x = 0 
                    self.is_off = True

                    for i in range( strip.numPixels() ) : 
                        strip.setPixelColor(i, Color(0, 0, 0)) 
                        strip.show()
                    pass
                pass
            else : 
                self.is_off = False
            pass
            
            if light_type == 'static': 
                for i in range(numPixels):
                    strip.setPixelColor(i, rgb)
                pass
                strip.show()
                sleep(0.05)
            elif light_type == 'breath':  
                fx = f(x)

                red = int(((rgb & 0x00ff00)>>8) * fx)
                green = int(((rgb & 0xff0000) >> 16) * fx)
                blue = int((rgb & 0x0000ff) * fx )
                _rgb = int((red << 8) | (green << 16) | blue)

                for i in range(numPixels):
                    strip.setPixelColor(i, _rgb)     
                    strip.show()
                pass

                x += 1
                
                if x > 200:
                    x = 0 
                    for i in range(numPixels):
                        strip.setPixelColor(i, 0)     
                        strip.show()
                    pass
                pass

                sleep(0.02)
            elif light_type == 'flash':
                for i in range(numPixels):
                    strip.setPixelColor(i, rgb)     
                    strip.show()
                pass
                sleep(flashTime[flashTimeIndex])

                for i in range(numPixels):
                    strip.setPixelColor(i, 0)     
                    strip.show()
                pass
                sleep(flashTime[flashTimeIndex])
                
                flashTimeIndex += 1
                if flashTimeIndex >= len(flashTime):
                    flashTimeIndex = 0
                pass
            pass
        pass # loop

        log.info( "End loop" )
        
        self._running = False
        self._thread = None 
    pass # -- _lightLoop
    
pass

if __name__ == "__main__":
    rgb_led = RGB_LED()
    #rgb_led.begin()

    def handler(signal, frame):
        print( "", flush=True) 

        log.info('You have pressed Ctrl-C.')

        rgb_led.finish()

        sleep( 0.5 ) 
    pass

    signal.signal(signal.SIGINT, handler)

    # turn on
    rgb_led.setPixelColor(0, Color(255, 0, 0))       #Red
    rgb_led.setPixelColor(1, Color(0, 255, 0))       #Green
    rgb_led.setPixelColor(2, Color(0, 0, 255))       #Blue
    rgb_led.setPixelColor(3, Color(255, 255, 0))     #Yellow
    rgb_led.show()

    sleep(2)

    rgb_led.light_effect( "static", Color(255, 255, 0) )
    sleep( 3 )

    rgb_led.light_effect( "breath", Color(255, 0, 0) )
    sleep( 3 )

    rgb_led.light_effect( "flash", Color(0, 255, 0) )
    sleep( 3 )

    # remove light_effect 
    rgb_led.turn_off()

    # turn off 
    rgb_led.setPixelColor(0, Color(0, 0, 0))       #Red
    rgb_led.setPixelColor(1, Color(0, 0, 0))       #Green
    rgb_led.setPixelColor(2, Color(0, 0, 0))       #Blue
    rgb_led.setPixelColor(3, Color(0, 0, 0))       #Yellow
    rgb_led.show() 

    rgb_led.join()

pass


