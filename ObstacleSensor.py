import RPi.GPIO as GPIO, threading
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
        GPIO.cleanup( self.RIGHT_GPIO ) 
        GPIO.cleanup( self.LEFT_GPIO ) 
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

            left_obstacle = GPIO.input( self.LEFT_GPIO ) == 0 
            right_obstacle = GPIO.input( self.RIGHT_GPIO ) == 0 
            
            if not left_obstacle and not right_obstacle :
                # 장애물이 없을 때
                log.info( "forward")
                robot.forward() 
                sleep( 0.01 ) 
                robot.stop()
                sleep( 0.01 )
            else :
                # 왼쪽에 장애물이 있을 때
                log.info( f"LEFT = {left_obstacle:d}, RIGHT = {right_obstacle:d}" )

                if left_obstacle and left_obstacle :
                    # 양쪽에 장애물이 있을 때
                    robot.backward()
                    sleep( 0.01 )
                    robot.left()
                    sleep( 0.01 )
                    robot.stop()
                    sleep( 0.01 )
                elif left_obstacle :                 
                    robot.right()
                    sleep( 0.01 )
                    robot.stop()
                    sleep( 0.01 ) 
                elif right_obstacle :                 
                    robot.left()
                    sleep( 0.015 )
                    robot.stop()
                    sleep( 0.01 ) 
                pass
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
