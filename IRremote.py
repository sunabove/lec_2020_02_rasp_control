import RPi.GPIO as GPIO, threading
from time import sleep
from AlphaBot2 import AlphaBot2

class IRremote : 

    IR_GPIO_NO = 17

    def __init__(self, robot) : 
        self.robot = robot 

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IR_GPIO_NO, GPIO.IN)

        self._running = False 

        self._thread = threading.Thread(target=self.process_signal, args=[] )
        self._thread.start()
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        GPIO.cleanup( self.IR_GPIO_NO )

        self._running = False 
        _thread = self._thread 
        if _thread is not None :
            _thread.join()

            self._thread = None 
        pass
    pass # -- finish

    def _getkey(self):

        gpio_no = self.IR_GPIO_NO

        if GPIO.input(gpio_no) == 0:
            count = 0
            while GPIO.input(gpio_no) == 0 and count < 200:  #9ms
                count += 1
                time.sleep(0.00006) 
            if(count < 10):
                return;
            count = 0
            while GPIO.input(gpio_no) == 1 and count < 80:  #4.5ms
                count += 1
                time.sleep(0.00006)
            pass

            idx = 0
            cnt = 0
            data = [0,0,0,0]
            for i in range(0,32):
                count = 0
                while GPIO.input(gpio_no) == 0 and count < 15:    #0.56ms
                    count += 1
                    time.sleep(0.00006)
                    
                count = 0
                while GPIO.input(gpio_no) == 1 and count < 40:   #0: 0.56mx
                    count += 1                               #1: 1.69ms
                    time.sleep(0.00006)
                    
                if count > 7:
                    data[idx] |= 1<<cnt
                if cnt == 7:
                    cnt = 0
                    idx += 1
                else:
                    cnt += 1
                pass
            pass

            # print data
            if data[0]+data[1] == 0xFF and data[2]+data[3] == 0xFF:  #check
                return data[2]
            else:
                print("repeat")
                return "repeat"
            pass
        pass
    pass # -- _getkey

    def process_signal(self) :
        try:
            self._process_signal()
        except KeyboardInterrupt:
            self._running = False 
            self._thread = None 
        finally:
            pass
        pass
    pass # -- process_signal

    def _process_signal(self) :
        self._running = True

        robot = self.robot
        n = 0 

        while self._running :
            key = self._getkey()

            if key is None :
                n += 1
                if n > 20_000:
                    n = 0
                    robot.stop()
                pass
            else : 
                n = 0                 
                if key == 0x18:
                    robot.forward()
                    print("forward")
                elif key == 0x08:
                    robot.left()
                    print("left")
                elif key == 0x1c:
                    robot.stop()
                    print("stop")
                elif key == 0x5a:
                    robot.right()
                    print("right")
                elif key == 0x52:
                    robot.backward()        
                    print("backward")
                elif key == 0x15:
                    robot.speed_up( 10 ) 
                elif key == 0x07:
                    robot.speed_up( -10 ) 
                pass 
            pass
        pass # -- while

        self._running = False 
        self._thread = None 
    pass # -- _process_signal

if __name__ == '__main__':
    print( "Hello..." )
    print( 'IRremote Test Start ...' )

    GPIO.setwarnings(False)

    robot = AlphaBot2()

    irremote = IRremote( robot )

    robot.stop() 

    GPIO.cleanup();

    print( "Good bye!")
pass