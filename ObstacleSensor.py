import RPi.GPIO as GPIO
from time import sleep

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class ObstacleSensor : 

    DR = 16
    DL = 19

    def __init__(self, robot) : 
        self.robot = robot 

        GPIO.setmode(GPIO.BCM)
        GPIO.setup( self.DR, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup( self.DL, GPIO.IN, GPIO.PUD_UP)

        self._repeat_cnt = 0 

        self._running = False 

        self._thread = threading.Thread(target=self.process_signal, args=[] )
        self._thread.start()
    pass

    def join(self) :
        _thread = self._thread 
        if _thread :
            _thread.join()
        pass
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
        GPIO.cleanup( self.DR ) 
        GPIO.cleanup( self.DL ) 
    pass # -- finish 

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

    def _process_signal(self) :
        self._running = True

        robot = self.robot
        n = 0 

        idx = 0 

        robot = self.robot

        while self._running :
            idx += 1

            DL_status = GPIO.input( self.DL )
            DR_status = GPIO.input( self.DR )        
            
            if DL_status == 0 or DR_status == 0 :
                print( f"DL = {DL_status}, DR = {DR_status}" )

                robot.left()
                sleep( 0.02 )
                robot.stop()
                sleep( 0.02 )
            else:
                robot.forward() 
                sleep( 0.01 ) 
            pass
        pass  

        self._running = False 
        self._thread = None 
    pass # -- _process_signal

pass # --ObstacleSensor

if __name__ == '__main__':
    log.info( "Hello..." )
    log.info( 'IRremote Test Start ...' )

    GPIO.setwarnings(False)

    from AlphaBot2 import AlphaBot2 

    robot = AlphaBot2()

    obstacleSensor = ObstacleSensor( robot )

    def handler(signal, frame):
        print()
        sleep( 0.01 )

        log.info('You have pressed Ctrl-C.')

        obstacleSensor.finish()

        sleep( 0.5 ) 
    pass

    import signal
    signal.signal(signal.SIGINT, handler)

    obstacleSensor.join()

    robot.stop() 

    GPIO.cleanup();

    log.info( "Good bye!")
pass
