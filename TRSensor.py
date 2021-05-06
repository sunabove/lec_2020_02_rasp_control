# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time, inspect, numpy as np

from time import sleep

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class TRSensor :

    CS = 5
    Clock = 25
    Address = 24 
    DataOut = 23
    Button = 7

    def __init__(self, white = 540, black=240, num_sensors = 5 ):
        self.white = white
        self.black = black
        self.num_sensors = num_sensors
        self.idx = 0 
        self.prev_pos = 0

        self.calibratedMin = [0] * num_sensors
        self.calibratedMax = [1023] * num_sensors
        self.last_value = 0
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.Clock, GPIO.OUT)
        GPIO.setup(self.Address, GPIO.OUT)
        GPIO.setup(self.CS, GPIO.OUT)
        GPIO.setup(self.DataOut, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(self.Button, GPIO.IN, GPIO.PUD_UP)
    pass # -- __init__

    def __del__(self):
        self.finish()
    pass

    def finish(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for port in [ self.Clock, self.Address, self.CS, self.DataOut, self.Button ] :             
            GPIO.cleanup(port)
        pass
    pass # -- finish

    def read_analog(self):
        num_sensors = self.num_sensors

        value = [0]*(num_sensors + 1)
        #Read Channel 0~channel 6 AD value
        
        cs = self.CS
        address = self.Address
        dataOut = self.DataOut
        clock = self.Clock

        for s in range(0, num_sensors + 1):
            GPIO.output( cs, GPIO.LOW )

            for i in range(0, 4):
                #sent 4-bit Address
                if ((s) >> (3 - i)) & 0x01 :
                    GPIO.output(address, GPIO.HIGH)
                else:
                    GPIO.output(address, GPIO.LOW)
                pass

                #read MSB 4-bit data
                value[s] <<= 1

                if(GPIO.input(dataOut)):
                    value[s] |= 0x01
                pass

                GPIO.output(clock, GPIO.HIGH)
                GPIO.output(clock, GPIO.LOW)
            pass

            for i in range(0, 6):
                #read LSB 8-bit data
                value[s] <<= 1

                if GPIO.input(dataOut) :
                    value[s] |= 0x01
                pass

                GPIO.output(clock, GPIO.HIGH)
                GPIO.output(clock, GPIO.LOW)
            pass

            time.sleep(0.0001)
            GPIO.output(cs,GPIO.HIGH)
        pass

        return np.array( value[1:] )
    pass # -- read_analog

    def calibrate(self):
        num_sensors = self.num_sensors

        max_sensor_values = [0]*num_sensors
        min_sensor_values = [0]*num_sensors

        for j in range(0,10):
        
            sensor_values = self.read_analog();
            
            for i in range(0, num_sensors):
            
                # set the max we found THIS time
                if((j == 0) or max_sensor_values[i] < sensor_values[i]):
                    max_sensor_values[i] = sensor_values[i]
                pass

                # set the min we found THIS time
                if((j == 0) or min_sensor_values[i] > sensor_values[i]):
                    min_sensor_values[i] = sensor_values[i]
                pass
            pass
        pass

        # record the min and max calibration values
        for i in range(0, num_sensors):
            if(min_sensor_values[i] > self.calibratedMin[i]):
                self.calibratedMin[i] = min_sensor_values[i]
            pass

            if(max_sensor_values[i] < self.calibratedMax[i]):
                self.calibratedMax[i] = max_sensor_values[i]
            pass
        pass
    pass # -- calibrate

    def read_calibrated(self):
        value = 0
        #read the needed values
        sensor_values = self.read_analog();

        num_sensors = self.num_sensors

        for i in range (0, num_sensors):
            denominator = self.calibratedMax[i] - self.calibratedMin[i]

            if(denominator != 0):
                value = (sensor_values[i] - self.calibratedMin[i])* 1000 / denominator
            pass
            
            if(value < 0):
                value = 0
            elif(value > 1000):
                value = 1000
            pass
            
            sensor_values[i] = value
        pass
        
        return sensor_values
    pass # -- read_calibrated

    def read_line(self, white_line = 0):

        sensors = self.read_calibrated()

        num_sensors = self.num_sensors

        avg = 0
        sum = 0
        on_line = 0

        for i in range(0, num_sensors):
            value = sensors[i]
            if(white_line):
                value = 1000-value
            pass

            # keep track of whether we see the line at all
            if value > 200 :
                on_line = 1
            pass
                
            # only average in values that are above a noise threshold
            if value > 50 :
                avg += value * (i * 1000);  # this is for the weighted total,
                sum += value;                  #this is for the denominator 
            pass
        pass

        if on_line != 1 :
            if self.last_value < (num_sensors - 1)*1000/2 :
                # If it last read to the left of center, return 0.            
                #print("left")
                self.last_value = 0;
            else:
                # If it last read to the right of center, return the max.            
                #print("right")
                self.last_value = (num_sensors - 1)*1000
            pass
        else:
            self.last_value = avg/sum
        pass
        
        return self.last_value, sensors
    pass # -- read_line

    def read_sensor(self, debug=1) : 
        self.idx += 1

        idx = self.idx
        
        # 신호 읽기
        sensor = self.read_analog()

        # 신호 위치
        white = self.white
        black = self.black

        norm = self.normalize( sensor, white, black )
        pos = 1.0

        if debug : 
            sensor_text = ", ".join( [ f"{x:4}" for x in sensor ] )
            norm_text = ", ".join( [ f"{x:.2f}" for x in norm ] )
            road_text = self.to_sensors_text( norm, 5 )
        
            print( f"[{idx:04}] Sensor [ {sensor_text}  ] " )
            print( f"[{idx:04}] Normal [ {norm_text}  ] pos = {pos:.4}" )
            print( f"[{idx:04}] Line   [ {road_text} ]" )
            print()
        pass

        return pos, norm
    pass # -- read_sensor

    def normalize(self, sensor, white, black) :
        # 신호 위치
        pos = 0
        
        # normalize
        norm = np.zeros( len( sensor ), np.float32 )
        wb_diff = white - black

        for i, s in enumerate( sensor ):
            n = 0
            if s < black :
                n = 1 
            elif s > white :
                n = 0
            else :
                n = (white - s)/wb_diff
            pass

            norm[i] = n
        pass 

        return norm
    pass # -- normalize

    def to_sensors_text(self, norm, size=1) :
        txt = [ ]
        boxes = "▁▂▃▅▆▇"
        len_boxes = len( boxes )

        for n in norm :
            i = (len_boxes - 1)*n
            i = int( i + 0.5 )
            t = boxes[i]
            
            txt.append( t*size )
        pass

        return " ".join( txt  )
    pass # -- to_sensors_text

pass

if __name__ == '__main__':
    print("TRSensor")

    tr = TRSensor()

    def exit( result ) :
        tr.finish()
        sleep( 0.5 )  
    pass

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        print('You have pressed Ctrl-C.')

        exit( 0 )

        print( "Good bye!")

        import sys
        sys.exit( 0 )
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        tr.read_sensor() 
        time.sleep(0.2) 
    pass
pass