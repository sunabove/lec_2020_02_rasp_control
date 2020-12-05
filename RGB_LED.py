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

    def __init__(self, debug=False) : 
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

        self.debug = debug
        self.req_no = 0  
    
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

        self.strip.begin()
        self.strip.show()
    pass

    def __del__(self):
        self.finish()
    pass

    def finish( self ) :
        self.turn_off()

        self.join()
    pass

    def join(self) :
        # 실행중인 쓰레드가 끝날 때까지 기다린다.
        self.req_no += 1 
        self.running = False 

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

    def turn_off(self):
        log.info(inspect.currentframe().f_code.co_name) 

        self.join()

        self.running = False  
        self.req_no += 1 
        
        strip = self.strip 
        numPixels = strip.numPixels()
        for i in range(numPixels): 
            strip.setPixelColor(i, Color(0, 0, 0)) 
            strip.show()
        pass

        sleep( 0.1 )
    pass 

    def light_effect(self, light_type="", rgb=Color(0,0,0), duration=None):
        log.info(inspect.currentframe().f_code.co_name) 
        log.info( f"light_type: {light_type}" )

        time_to = None 
        if duration is not None :
            time_to = time.time() + duration
        pass

        args = [ light_type, rgb, time_to ]
        self._thread = threading.Thread(target = self._lightLoop, args=args)
        self._thread.start()
    pass 

    def _lightLoop(self, light_type="", rgb=Color(0,0,0), time_to=None):
        log.info(inspect.currentframe().f_code.co_name) 

        self.req_no += 1 

        req_no = self.req_no

        x = 0
        flashTimeIndex = 0 

        strip = self.strip 
        numPixels = strip.numPixels()

        is_off = False 

        self.running = True
        
        while req_no == self.req_no and self.running : 

            if time_to is not None :
                # 일정 시간이 지나면, LED를 끈다.
                now = time.time()

                if now > time_to and light_type is not None :
                    time_to = None 
                    light_type = None
                    rgb = Color( 0, 0, 0 ) 

                    self.running = False 
                else :
                    sleep( 0.1 )
                pass
            pass 

            if light_type is None :
                if is_off is False :
                    x = 0 
                    is_off = True

                    for i in range(numPixels): 
                        strip.setPixelColor(i, Color(0, 0, 0)) 
                        strip.show()
                    pass
                pass
            else : 
                is_off = False
            pass
            
            if light_type == 'static': 
                self.static_light( req_no, rgb )
            elif light_type == 'breath':  
                x = self.breath_light( req_no, rgb, x )
            elif light_type == 'flash':
                flashTimeIndex = self.flash_light( req_no, rgb, flashTimeIndex )
            pass
        pass # loop

        log.info( "end light_loop" )
        
        self._thread = None 
    pass # -- _lightLoop

    def static_light(self, req_no, rgb=Color(0,0,0) ) : 
        log.info(inspect.currentframe().f_code.co_name)

        strip = self.strip 
        numPixels = strip.numPixels()

        for i in range(numPixels):
            strip.setPixelColor(i, rgb)
        pass
        strip.show()
        
        self.running = False
    pass # -- static_light

    def breath_light(self, req_no, rgb=Color(0,0,0), x = 0 ) : 
        debug = self.debug
        debug and log.info(inspect.currentframe().f_code.co_name)

        strip = self.strip 
        numPixels = strip.numPixels() 

        fx = (-1/10000.0)*x*x + (1/50.0)*x 

        red = int(((rgb & 0x00ff00)>>8) * fx)
        green = int(((rgb & 0xff0000) >> 16) * fx)
        blue = int((rgb & 0x0000ff) * fx )
        _rgb = int((red << 8) | (green << 16) | blue)

        for i in range(numPixels):
            if self.running and req_no == self.req_no : 
                strip.setPixelColor(i, _rgb)     
                strip.show()
            pass
        pass

        x += 1
        
        if x > 200:
            x = 0 
            for i in range(numPixels):
                if self.running and req_no == self.req_no : 
                    strip.setPixelColor(i, 0)     
                    strip.show()
                pass
            pass
        pass

        if self.running and req_no == self.req_no : 
            sleep(0.02)
        pass

        return x 
    pass # -- breath_light

    def flash_light(self, req_no, rgb=Color(0,0,0), flashTimeIndex = 0 ) : 
        debug = self.debug
        debug and log.info(inspect.currentframe().f_code.co_name)

        strip = self.strip 
        numPixels = strip.numPixels()

        flashTime = [0.3, 0.2, 0.1, 0.05, 0.05, 0.1, 0.2, 0.5, 0.2] 

        for i in range(numPixels):
            if self.running and req_no == self.req_no : 
                strip.setPixelColor(i, rgb)     
                strip.show()
            pass
        pass

        if self.running and req_no == self.req_no : 
            sleep(flashTime[flashTimeIndex])
        pass
        
        for i in range(numPixels):
            if self.running and req_no == self.req_no : 
                strip.setPixelColor(i, 0)     
                strip.show()
            pass
        pass

        if self.running and req_no == self.req_no : 
            sleep(flashTime[flashTimeIndex])
        pass

        flashTimeIndex += 1

        if flashTimeIndex >= len(flashTime):
            flashTimeIndex = 0
        pass

        return flashTimeIndex

    pass # -- flash_light

pass

if __name__ == "__main__":
    rgb_led = RGB_LED()
    #rgb_led.begin()

    def handler(signal, frame):
        print( "", flush=True) 

        log.info('You have pressed Ctrl-C.')

        rgb_led.finish()
    pass

    signal.signal(signal.SIGINT, handler)

    # turn on
    rgb_led.setPixelColor(0, Color(255, 0, 0))       #Red
    rgb_led.setPixelColor(1, Color(0, 255, 0))       #Green
    rgb_led.setPixelColor(2, Color(0, 0, 255))       #Blue
    rgb_led.setPixelColor(3, Color(255, 255, 0))     #Yellow
    rgb_led.show()

    sleep(2)

    if 0 : 
        rgb_led.light_effect( "static", Color(255, 255, 0) )
        sleep( 3 )
    pass

    rgb_led.light_effect( "breath", Color(0, 255, 0) )
    sleep( 3 )

    if 0 : 
        rgb_led.light_effect( "flash", Color(0, 255, 0) )
        sleep( 3 )
    pass

    # remove light_effect 
    rgb_led.turn_off()

    # turn off 
    rgb_led.setPixelColor(0, Color(0, 0, 0))       #Red
    rgb_led.setPixelColor(1, Color(0, 0, 0))       #Green
    rgb_led.setPixelColor(2, Color(0, 0, 0))       #Blue
    rgb_led.setPixelColor(3, Color(0, 0, 0))       #Yellow
    rgb_led.show() 

    input( "Enter to quit!")
pass


