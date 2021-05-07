# coding: utf-8

import RPi.GPIO as GPIO, time, threading , inspect
from time import sleep
from gpiozero import Buzzer
from ObstacleSensor import ObstacleSensor
from LineTracker import LineTracker

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class IRRemote :

    GPIO_NO = 17

    def __init__(self, robot, buzzer=None, obstacleSensor=None, lineTracker=None):

        self.robot = robot
        
        if buzzer is None : 
            self.buzzer = Buzzer(4)
        elif buzzer is not None : 
            self.buzzer = buzzer
        pass

        self.obstacleSensor = obstacleSensor if obstacleSensor else ObstacleSensor( robot )
        self.lineTracker = lineTracker if lineTracker else LineTracker( robot )

        self.prev_key = 0 
        self.repeat_cnt = 0 

        self.decoding = False
        self.pList = []
        self.timer = time.time()
        
        self.callback = self.print_ir_code

        self.checkTime = 150  # time in milliseconds
        
        self.repeatCodeOn = True
        self.lastIRCode = 0
        self.maxPulseListLength = 70

        self.running = True 
        self.thread = False

        GPIO.setwarnings(False)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_NO, GPIO.IN)
        GPIO.add_event_detect(self.GPIO_NO, GPIO.BOTH, callback=self.detect_gpio)

        time.sleep( 0.1 )

        log.info('Setting up callback')
        
        self.callback = self.remote_callback
        self.set_repeat(True)    
    pass # -- init

    def __del__(self):
        self.finish()
    pass
    
    def finish(self):
        self.running = False 

        thread = self.thread
        if thread is not None :
            thread.join()
        pass

        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup(self.GPIO_NO)
    pass # -- finish

    def detect_gpio(self, pin):
        self.pList.append(time.time()-self.timer)
        self.timer = time.time()        

        if self.decoding == False and self.running :
            self.decoding = True

            self.thread = threading.Thread(name='self.pulse_checker',target=self.pulse_checker)
            self.thread.start()
        return
    pass

    def pulse_checker(self):
        timer = time.time()
        debug = False 

        while self.running :                
            check = (time.time()-timer)*1000

            if check > self.checkTime:                    
                debug and log.info( f"check={check}, pList len={len(self.pList)}" )
                break
            elif len(self.pList) > self.maxPulseListLength:
                debug and log.info( f"check={check}, pList len={len(self.pList)}" )
                break
            pass

            sleep(0.001)
        pass

        if len(self.pList) > self.maxPulseListLength:
            decode = self.decode_pulse(self.pList)
            self.lastIRCode = decode
        elif len(self.pList) < 10:        
            if self.repeatCodeOn == True:
                decode = self.lastIRCode
            else:
                decode = 0
                self.lastIRCode = decode
            pass
        else:
            decode = 0
            self.lastIRCode = decode
        pass

        self.pList = []
        self.decoding = False

        if self.callback is not None and self.running :
            self.callback( decode )
        pass
        
        return
    pass # -- pulse_checker

    def decode_pulse(self, pList):

        bitList = []
        sIndex = -1
        
        for p in range(0,len(pList)):
            try:
                pList[p]=float(pList[p])*1000

                if pList[p]<11:
                    if sIndex == -1:
                        sIndex = p
                    pass
                pass
            except:
                pass
            pass
        pass

        if sIndex == -1:
            return -1
        elif sIndex+1 >= len(pList):
            return -1        
        elif (pList[sIndex]<4 or pList[sIndex]>11):
            return -1
        elif (pList[sIndex+1]<2 or pList[sIndex+1]>6):
            return -1
        pass

        for i in range(sIndex+2,len(pList),2):
            if i+1 < len(pList):
                if pList[i+1]< 0.9:  
                    bitList.append(0)
                elif pList[i+1]< 2.5:
                    bitList.append(1)
                elif (pList[i+1]> 2.5 and pList[i+1]< 45):
                    #print('end of data found')
                    break
                else:
                    break
                pass
            pass
        pass

        # convert the list of 1s and 0s into a
        # binary number

        pulse = 0
        bitShift = 0

        for b in bitList:
            pulse = (pulse<<bitShift) + b
            bitShift = 1
        pass

        return pulse
    pass

    def print_ir_code(self, code):
        log.info( f"ir_code = {hex(code)}" )

        return
    pass

    def set_repeat(self, repeat = True):
        self.repeatCodeOn = repeat

        return
    pass

    def beep_warning(self) :
        import Functions as fun
        fun.beep_warning()
    pass

    def system_shutdown(self) :
        log.info(inspect.currentframe().f_code.co_name) 

        # 시스템 셧다운
        # 경고음
        self.beep_warning()

        from subprocess import check_call

        check_call(['sudo', 'poweroff'])
    pass # system_shutdown

    def remote_callback(self, key ):
        log.info( f"key = {hex(key)}" )

        if key and self.prev_key == key :
            self.repeat_cnt += 1
        elif key :
            self.repeat_cnt = 0 
        pass

        robot = self.robot

        obstacleSensor = self.obstacleSensor
        lineTracker = self.lineTracker

        if key == 0xff38c7 :
            log.info( f'stop')
            
            robot.stop()

            obstacleSensor.is_running() and obstacleSensor.stop()
            lineTracker.is_running() and lineTracker.stop()

            robot.stop()
        elif key in [ 0xff9867, 0xff18e7 ]:
            log.info( f"forward" ) 
            robot.forward()
        elif key in [ 0xff4ab5 , 0xff42bd, 0xff52ad ]:
            log.info( f'backward' )
            robot.backward()
        elif key in [ 0xff10ef, 0xff30cf, 0xff6897 ]:
            log.info( f'left' )
            robot.left()
        elif key in [ 0xff5aa5, 0xff7a85, 0xffb04f ]:
            log.info( f'right' )
            robot.right()
        elif key == 0xffa857 :
            log.info( f"speed up" )
            robot.speed_up( 5 )
        elif key == 0xffe01f:
            log.info( f'speed down')
            robot.speed_down( 5 )
        elif key == 0xffe21d : # shutdown 
            log.info( f"shut down, repeat_cnt={self.repeat_cnt}" )
            if self.repeat_cnt > 10 : 
                self.system_shutdown()
            pass
        elif key == 0xffa25d : # obstacle avoidance
            log.info( f'Obstacle Sensor')

            lineTracker.is_running() and lineTracker.stop()

            if obstacleSensor.is_running() :
                log.info( "Obstacle Sensor is running already." )
            else :
                log.info( "Obstacle Sensor start" )
                obstacleSensor.start() 
            pass
        elif key == 0xff629d : # line tracker
            log.info( "Line Tracker" )

            if lineTracker.is_running() :
                log.info( "LineTracker is running already." )
            else :
                log.info( "LineTracker start")
                lineTracker.start()
            pass
        pass

        if type( key ) == int : 
            self.prev_key = key 
        pass
    pass

pass

if __name__ == "__main__":

    log.info('Starting IR remote senssor ...')

    from Motor import Motor

    robot = Motor()
    
    ir = IRRemote( robot )  
            
    input( "Enter to quit..." )

    log.info('Removing callback and cleaning up GPIO') 

pass # -- main