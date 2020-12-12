# coding: utf-8

import RPi.GPIO as GPIO
import time, threading 
from time import sleep

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class IRSensor :    

    def __init__(self):        

        self.decoding = False
        self.pList = []
        self.timer = time.time()
        
        self.callback = self.print_ir_code

        self.checkTime = 150  # time in milliseconds
        self.verbose = False
        self.repeatCodeOn = True
        self.lastIRCode = 0
        self.maxPulseListLength = 70

        self.running = True 
        self.thread = False
    pass

    def __del__(self):
        self.running = False 

        thread = self.thread
        if thread is not None :
            thread.join()
        pass
    pass

    def pWidth(self, pin):
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

        while self.running :                
            check = (time.time()-timer)*1000

            if check > self.checkTime:                    
                self.verbose and print(check, len(self.pList))
                break
            pass

            if len(self.pList) > self.maxPulseListLength:
                self.verbose and print(check, len(self.pList))
                break
            pass

            sleep(0.001)
        pass

        if len(self.pList) > self.maxPulseListLength:
            decode = self.decode_pulse(self.pList)
            self.lastIRCode = decode
        elif len(self.pList) < 10:
            # if the length of self.pList is less than 10
            # assume repeat code found
        
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

        if self.callback != None and self.running :
            self.callback(decode)
        pass
        
        return
    pass

    def decode_pulse(self,pList):

        bitList = []
        sIndex = -1

        # convert the timespans in seconds to milli-seconds
        # look for the start of the IR remote signal
        
        for p in range(0,len(pList)):
            try:
                pList[p]=float(pList[p])*1000

                if self.verbose == True:
                    print(pList[p])
                if pList[p]<11:
                    if sIndex == -1:
                        sIndex = p
                    pass
                pass
            except:
                pass
            pass
        pass

        # if no acceptable start is found return -1

        if sIndex == -1:
            return -1

        if sIndex+1 >= len(pList):
            return -1
        
        if (pList[sIndex]<4 or pList[sIndex]>11):
            return -1

        if (pList[sIndex+1]<2 or pList[sIndex+1]>6):
            return -1

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

        if self.verbose == True:
            log.info( f"bitList = {bitList}" )
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

    def set_callback(self, callback = None):
        """set_callback, function to allow the user to set
        or change the callback function used at any time"""

        self.callback = callback

        return
    pass

    def remove_callback(self):
        """remove_callback, function to allow the user to remove
        the callback function used at any time"""

        self.callback = None

        return
    pass

    def print_ir_code(self, code):
        """print_ir_code, function to display IR code received"""

        log.info( f"ir_code = {hex(code)}" )

        return
    pass

    def set_verbose(self, verbose = True):
        self.verbose = verbose

        return
    pass

    def set_repeat(self, repeat = True):
        self.repeatCodeOn = repeat

        return
    pass

pass

if __name__ == "__main__":

    def remote_callback(code):
        print( f"code = {hex(code)}" )

        if code == 0x10EFD827:
            print("Power")
        elif code == 0x10EFF807:
            print('A')
        elif code == 0x10EF7887:
            print('B')
        elif code == 0x10EF58A7:
            print('C')
        elif code == 0x10EFA05F:
            print('Up Arrow')
        elif code == 0x10EF00FF:
            print('Down Arrow')
        elif code == 0x10EF10EF:
            print('Left Arrow')
        elif code == 0x10EF807F:
            print('Right Arrow')
        elif code == 0x10EF20DF:
            print('Select')
        else:
            print('.')  # unknown code
        pass

        return
    pass

    ir = IRSensor( )  
            
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # uses numbering outside circles
    GPIO.setup(17,GPIO.IN)   # set pin 16 to input
    GPIO.add_event_detect(17,GPIO.BOTH,callback=ir.pWidth)

    ir.set_verbose()
    print('Starting IR remote sensing using DECODE function')

    time.sleep(5)
    print('Setting up callback')
    ir.set_verbose(False)
    ir.set_callback(remote_callback)
    ir.set_repeat(True)

    input( "Enter to quit..." )

    print('Removing callback and cleaning up GPIO')
    ir.remove_callback()
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup(16)

pass # -- main