import RPi.GPIO as GPIO, threading, signal, time, inspect
from time import sleep

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class ObstacleSensor : 

    RIGHT_GPIO = 16   # 오른 쪽 센서 GPIO 번호
    LEFT_GPIO = 19    # 왼쪽 센서 GPIO 번호 

    def __init__(self, robot) : 
        self.robot = robot 

        GPIO.setmode(GPIO.BCM)
        GPIO.setup( self.RIGHT_GPIO, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup( self.LEFT_GPIO, GPIO.IN, GPIO.PUD_UP)

        self._repeat_cnt = 0 

        self._running = False 

        self._thread = threading.Thread(target=self._process_signal, args=[] )
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
        GPIO.cleanup( self.RIGHT_GPIO ) 
        GPIO.cleanup( self.LEFT_GPIO ) 
    pass # -- finish 

    def _process_signal(self) :
        try:
            self._process_signal_imp()
        except Exception as e :
            self._running = False 
            self._thread = None 

            log.info( e )
        finally:
            pass
        pass
    pass # -- process_signal

    def _process_signal_imp(self) :
        self._running = True

        robot = self.robot
        n = 0 

        idx = 0 

        robot = self.robot
        
        then = time.time()
        interval = 0.02

        pre_state = -1

        while self._running :
            now = time.time()
            elapsed = now - then             

            if elapsed < interval : 
                sleep( interval - elapsed )
            else :
                then = now 

                idx += 1

                left_obstacle = GPIO.input( self.LEFT_GPIO ) == 0 
                right_obstacle = GPIO.input( self.RIGHT_GPIO ) == 0 

                state = 2*left_obstacle + right_obstacle

                if state == pre_state :
                    # do nothing
                    sleep( 0.01 ) 
                else :
                    pre_state = state
                
                    if left_obstacle == 0 and right_obstacle == 0 :
                        # 장애물이 없을 때
                        #log.info( "forward")
                        robot.forward()  
                        if 0 : 
                            sleep(0.01)
                            robot.stop()
                            sleep( 0.02 )
                        pass
                    else :
                        # 장애물이 있을 때
                        log.info( f"LEFT = {left_obstacle:d}, RIGHT = {right_obstacle:d}" )

                        if left_obstacle and right_obstacle: # 양쪽에 장애가 있을 때 
                            robot.backward() 
                            sleep(0.1)
                            robot.left() 
                            sleep(0.2)
                        elif left_obstacle : # 왼쪽에 장애가 있을 때 
                            robot.right() 
                            sleep(0.1)
                        elif right_obstacle : # 오른쪽에 장애가 있을 때 
                            robot.left()  
                            sleep(0.15)
                        pass
                    pass
                pass
            pass
        pass  

        self._running = False 
        self._thread = None 
    pass # -- _process_signal_imp

pass # --ObstacleSensor

if __name__ == '__main__':
    log.info( "Hello..." )
    log.info( 'IRremote Test Start ...' )

    GPIO.setwarnings(False)

    from AlphaBot2 import AlphaBot2 
    from Motor import Motor 

    robot = AlphaBot2()

    obstacleSensor = ObstacleSensor( robot )

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        log.info('You have pressed Ctrl-C.')

        obstacleSensor.finish()

        sleep( 0.5 ) 
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    obstacleSensor.join()

    robot.stop() 

    GPIO.cleanup();

    log.info( "Good bye!")
pass
