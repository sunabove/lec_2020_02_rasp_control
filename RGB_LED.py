# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
from time import sleep
import time, threading

from rpi_ws281x import Adafruit_NeoPixel, Color

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

        strip.begin()
        strip.show()

        self.rgb = 0
        self.light_type = 'static' 

        self.t = threading.Thread(target = lightLoop)
        self.t.setDaemon(True)
        self.t.start()
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

    def lightLoop():
    	flashTime = [0.3, 0.2, 0.1, 0.05, 0.05, 0.1, 0.2, 0.5, 0.2]
        flashTimeIndex = 0 
        f = lambda x: (-1/10000.0)*x*x + (1/50.0)*x 
        x = 0
        while True:
            rgb = self.rgb
            light_type = self.light_type
        
            if light_type == 'static': 
                for i in range(0,strip.numPixels()):
                    strip.setPixelColor(i, rgb)
                pass
                strip.show()
                sleep(0.05)
            elif light_type == 'breath': 
                red = int(((rgb & 0x00ff00)>>8) * f(x))
                green = int(((rgb & 0xff0000) >> 16) * f(x))
                blue = int((rgb & 0x0000ff) * f(x))
                _rgb = int((red << 8) | (green << 16) | blue)
                for i in range(0,strip.numPixels()):
                    strip.setPixelColor(i, _rgb)     
                    strip.show()
                pass
                sleep(0.02)
                x += 1
                if x >= 200:
                    x = 0
                pass
            elif light_type == 'flash':
                for i in range(0,strip.numPixels()):
                    strip.setPixelColor(i, rgb)     
                    strip.show()
                pass
                sleep(flashTime[flashTimeIndex])
                for i in range(0,strip.numPixels()):
                    strip.setPixelColor(i, 0)     
                    strip.show()
                pass
                sleep(flashTime[flashTimeIndex])
                flashTimeIndex += 1
                if flashTimeIndex >= len(flashTime):
                    flashTimeIndex = 0
                pass
            pass
        pass
    pass # -- loop

pass

if __name__ == "__main__":
    rgb_led = RGB_LED()

    rgb_led.begin()
    rgb_led.setPixelColor(0, Color(255, 0, 0))       #Red
    rgb_led.setPixelColor(1, Color(0, 255, 0))       #Green
    rgb_led.setPixelColor(2, Color(0, 0, 255))       #Blue
    rgb_led.setPixelColor(3, Color(255, 255, 0))     #Yellow
    rgb_led.show()

    time.sleep(2)
    rgb_led.setPixelColor(0, Color(0, 0, 0))       #Red
    rgb_led.setPixelColor(1, Color(0, 0, 0))       #Green
    rgb_led.setPixelColor(2, Color(0, 0, 0))       #Blue
    rgb_led.setPixelColor(3, Color(0, 0, 0))       #Yellow
    rgb_led.show()
pass


