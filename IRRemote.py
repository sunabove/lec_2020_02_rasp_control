import RPi.GPIO as GPIO, threading, inspect, signal
from time import sleep, time

from gpiozero import Buzzer

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class IRRemote : 

    IR_GPIO_NO = 17

    def __init__(self, robot, buzzer=None) : 
        self.robot = robot
        
        if buzzer is None : 
            self.buzzer = Buzzer(4)
        elif buzzer is not None : 
            self.buzzer = buzzer
        pass

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IR_GPIO_NO, GPIO.IN)

        self._repeat_cnt = 0 

        self._running = False 
        self._thread = None

        self.start()
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self) :
        self._running = False 
        _thread = self._thread 
        if _thread is not None :
            _thread.join()

            self._thread = None 
        pass

        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup( self.IR_GPIO_NO ) 
    pass # -- finish

    def start(self):
        if not self._running and self._thread is None : 
            self._thread = threading.Thread(target=self.process_signal, args=[] )
            self._thread.start()
        pass
    pass

    def stop(self) :
        self._running = False
    pass

    def join(self) :
        _thread = self._thread 
        if _thread :
            _thread.join()
        pass
    pass

    def check_interval(self, interval=0.00006):
        then = time()
        now = time()
        duration = interval/10
        while now - then < interval :
            sleep( duration )

            now = time()
        pass
    pass

    def check_gpio_count(self, gpio_value, check_count = 0) :
        gpio_no = self.IR_GPIO_NO
        count = 0
        interval = 0.00006
        while GPIO.input(gpio_no) == gpio_value and count < check_count :
            count += 1
            self.check_interval( interval ) 
        pass

        return count 
    pass

    def _getkey(self):

        gpio_no = self.IR_GPIO_NO

        if GPIO.input(gpio_no) != 0:
            return 
        pass

        interval = 0.00006 
        
        count = 0

        count = self.check_gpio_count( 0, 200 ) #9ms

        if count < 10 :
            log.info( f"get key count = {count}" )
            return;
        pass

        count = self.check_gpio_count( 1, 80 ) #4.5ms
        
        idx = 0
        cnt = 0
        data = [0, 0, 0, 0]

        for i in range(0, 32):
            count = self.check_gpio_count( 0, 15 ) #0.56ms
            count = self.check_gpio_count( 1, 40 ) #0.56ms 
                
            if count > 7:
                data[idx] |= 1 << cnt
            pass
        
            if cnt == 7:
                cnt = 0
                idx += 1
            else:
                cnt += 1
            pass
        pass

        if data[0]+data[1] == 0xFF and data[2]+data[3] == 0xFF:
            self._repeat_cnt = 0 

            return data[2]
        else:
            self._repeat_cnt += 1
            log.info( f"repeat : {self._repeat_cnt}" )

            return "repeat"
        pass
    pass # -- _getkey

    def process_signal(self) :
        try:
            self._process_signal()
        except Exception as e :
            self._running = False 
            self._thread = None 

            log.info( e )
        finally:
            pass
        pass
    pass # -- process_signal

    def system_shutdown(self) :
        log.info(inspect.currentframe().f_code.co_name) 

        # 시스템 셧다운
        from subprocess import check_call

        for frq in range( 1, 6 + 1 ) : 
            t = 1/frq
            buzzer.beep(on_time=t, off_time=t/2, n = int(frq), background=False)
            sleep( 1 )
        pass

        buzzer.beep(on_time=2, off_time=1, n = 1, background=False)

        check_call(['sudo', 'poweroff'])
    pass # system_shutdown

    def _process_signal(self) :
        self._running = True

        robot = self.robot
        key_none_count = 0 

        prev_key = None
        repeat_cnt = 0 

        while self._running :
            key = self._getkey()

            if key and prev_key == key :
                repeat_cnt += 1
            else :
                repeat_cnt = 0 
            pass

            if key is None :
                key_none_count += 1
                if key_none_count > 20_000:
                    key_none_count = 0 
                pass
            else : 
                key_none_count = 0

                if type( key )  == int : 
                    log.info( f"key: 0x{key:02x}, repeat_cnt={repeat_cnt}" )
                else :
                    log.info( f"key: {key}, repeat_cnt={repeat_cnt}" )
                pass

                if key in [ 0x18, 0x19 ] :
                    log.info( f"forward" )
                    robot.forward() 
                elif key == 0x52:
                    log.info( f"backward" )
                    robot.backward() 
                elif key in [ 0x08, 0x16 ] :
                    log.info( f"left" )
                    robot.left() 
                elif key == 0x5a:
                    log.info( f"right" )
                    robot.right() 
                elif key == 0x1c:
                    log.info( f"stop" )
                    robot.stop() 
                elif key == 0x15 : 
                    log.info( f"speed up" )
                    robot.speed_up( 5 ) 
                elif key == 0x07:
                    log.info( f"speed down" )
                    robot.speed_up( -5 ) 
                elif key == 0x47:
                    log.info( f"shut down" )
                    if repeat_cnt > 10 : 
                        robot.stop()
                        self.system_shutdown()
                    pass
                pass
            pass
        pass # -- while

        self._running = False 
        self._thread = None 
    pass # -- _process_signal

pass # --IRRemote

if __name__ == '__main__':
    log.info( "Hello..." )
    log.info( 'IRremote Test Start ...' )

    GPIO.setwarnings(False)

    from AlphaBot2 import AlphaBot2 
    from Motor import Motor

    robot = Motor()

    irremote = IRRemote( robot )

    def signal_handler(signal, frame):
        print( "", flush=True) 

        log.info('You have pressed Ctrl-C.')

        irremote.finish()

        sleep( 0.5 ) 
    pass

    signal.signal(signal.SIGINT, signal_handler)

    irremote.join()

    robot.stop() 

    GPIO.cleanup();

    log.info( "Good bye!")
pass