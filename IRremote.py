import RPi.GPIO as GPIO
import time
from AlphaBot2 import AlphaBot2

class IRremote : 

    IR = 17
    PWM = 50
    
    def __init__(self, robot) : 
        self.robot = robot
        self.n=0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IR, GPIO.IN)
    pass

    def getkey():
        if GPIO.input(IR) == 0:
            count = 0
            while GPIO.input(IR) == 0 and count < 200:  #9ms
                count += 1
                time.sleep(0.00006) 
            if(count < 10):
                return;
            count = 0
            while GPIO.input(IR) == 1 and count < 80:  #4.5ms
                count += 1
                time.sleep(0.00006)
            pass

            idx = 0
            cnt = 0
            data = [0,0,0,0]
            for i in range(0,32):
                count = 0
                while GPIO.input(IR) == 0 and count < 15:    #0.56ms
                    count += 1
                    time.sleep(0.00006)
                    
                count = 0
                while GPIO.input(IR) == 1 and count < 40:   #0: 0.56mx
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
    pass

    def process_signal(self) :
        try:
            self._process_signal()
        except KeyboardInterrupt:
            pass
        pass
    pass 

    def _process_signal(self) :
        robot = self.robot
        while 1:
            key = self.getkey()

            if key is None :
                n += 1
                if n > 20000:
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
        pass 
    pass

if __name__ == '__main__':
    print('IRremote Test Start ...')

    GPIO.setwarnings(False)

    robot = AlphaBot2()

    irremote = IRremote( robot )

    robot.stop() 

    GPIO.cleanup();
pass