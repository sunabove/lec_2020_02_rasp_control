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

    def __init__(self, num_sensors = 5, thresh = 410):
        self.thresh = thresh
        self.num_sensors = num_sensors
        self.idx = 0 
        self.prev_pos = 0

        self.calibratedMin = [0] * num_sensors
        self.calibratedMax = [1023] * num_sensors
        self.last_value = 0
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.Clock,GPIO.OUT)
        GPIO.setup(self.Address,GPIO.OUT)
        GPIO.setup(self.CS,GPIO.OUT)
        GPIO.setup(self.DataOut,GPIO.IN,GPIO.PUD_UP)
        GPIO.setup(self.Button,GPIO.IN,GPIO.PUD_UP)
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

    """
    Reads the sensor values into an array. There *MUST* be space
    for as many values as there were sensors specified in the constructor.
    Example usage:
    unsigned int sensor_values[8];
    sensors.read(sensor_values);
    The values returned are a measure of the reflectance in abstract units,
    with higher values corresponding to lower reflectance (e.g. a black
    surface or a void).
    """
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
                    GPIO.output(address,GPIO.HIGH)
                else:
                    GPIO.output(address,GPIO.LOW)
                pass

                #read MSB 4-bit data
                value[s] <<= 1

                if(GPIO.input(dataOut)):
                    value[s] |= 0x01
                pass

                GPIO.output(clock,GPIO.HIGH)
                GPIO.output(clock,GPIO.LOW)
            pass

            for i in range(0, 6):
                #read LSB 8-bit data
                value[s] <<= 1

                if GPIO.input(dataOut) :
                    value[s] |= 0x01
                pass

                GPIO.output(clock,GPIO.HIGH)
                GPIO.output(clock,GPIO.LOW)
            pass

            time.sleep(0.0001)
            GPIO.output(cs,GPIO.HIGH)
        pass

        return np.array( value[1:][::-1] )
    pass # -- read_analog

    """
    Reads the sensors 10 times and uses the results for
    calibration.  The sensor values are not returned; instead, the
    maximum and minimum values found over time are stored internally
    and used for the read_calibrated() method.
    """
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

    """
    Returns values calibrated to a value between 0 and 1000, where
    0 corresponds to the minimum value read by calibrate() and 1000
    corresponds to the maximum value.  Calibration values are
    stored separately for each sensor, so that differences in the
    sensors are accounted for automatically.
    """
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
        
        #print("read_calibrated",sensor_values)
        return sensor_values
    pass # -- read_calibrated

    """
    Operates the same as read calibrated, but also returns an
    estimated position of the robot with respect to a line. The
    estimate is made using a weighted average of the sensor indices
    multiplied by 1000, so that a return value of 0 indicates that
    the line is directly below sensor 0, a return value of 1000
    indicates that the line is directly below sensor 1, 2000
    indicates that it's below sensor 2000, etc.  Intermediate
    values indicate that the line is between two sensors.  The
    formula is:

       0*value0 + 1000*value1 + 2000*value2 + ...
       --------------------------------------------
             value0  +  value1  +  value2 + ...

    By default, this function assumes a dark line (high values)
    surrounded by white (low values).  If your line is light on
    black, set the optional second argument white_line to true.  In
    this case, each sensor value will be replaced by (1000-value)
    before the averaging.
    """
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

    def to_sensors_text(self, sensor, thresh) :
        txt = ""
        for i in range( len(sensor) ) :
            s = sensor[i]
            t = " "
            if s > thresh :
                # white
                t = "#"
            else :
                # black
                t = "_"
            pass
            
            txt += t
        pass

        return txt 
    pass # -- to_sensors_text

    def read_sensor(self, debug=True) : 
        self.idx += 1

        idx = self.idx
        thresh = self.thresh

        # 신호 읽기
        sensor = self.read_analog()

        # 신호 위치
        pos, norm = self.sensor_pos(sensor, thresh)

        txt = self.to_sensors_text( sensor, thresh)
        road_state = ""
        move_state = ""

        if np.all( sensor > thresh ) :
            move_state = "STOP"
            road_state = "All White"
        elif np.all( sensor < thresh ) :
            move_state = "FORE"
            road_state = "All Black"
        else :
            move_state = "MIX "
            road_state = "Mixed"
        pass

        debug and log.info( f"{sensor} {txt} [{move_state}] {road_state}" )
        debug and log.info( f"{norm} pos = {pos}" )

        return sensor
    pass # -- read_sensor

    def sensor_pos(self, sensor, thresh) :
        # 신호 위치
        pos = 0
        
        # normalize
        norm = np.array( sensor )

        for i, s in enumerate( sensor ):
            norm[i] = 1 if s > thresh else 0 
        pass

        # -- nomalize

        len_norm = len(norm)
        mid = len_norm // 2

        dir = 0 

        left_pos  = np.sum( [ n*(len_norm - i) for i, n in enumerate( norm ) ] )
        right_pos = np.sum( [ n*(i + 1) for i, n in enumerate( norm ) ] )
        
        if left_pos > right_pos : 
            pos = - np.sum( norm )
        elif left_pos < right_pos : 
            pos = np.sum( norm )
        elif np.all( norm == 1 ) :
            pos = -5 if self.prev_pos < 0 else  5
        else :
            pos = 0
        pass 

        #pos = pos / len_norm

        if pos != self.prev_pos :
            self.prev_pos = pos
        pass

        return pos, norm
    pass # -- sensor_pos

pass

if __name__ == '__main__':
    log.info("TRSensor")

    tr = TRSensor(thresh=410)

    def exit( result ) :
        tr.finish()
        sleep( 0.5 )  
    pass

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        log.info('You have pressed Ctrl-C.')

        exit( 0 )

        log.info( "Good bye!")

        import sys
        sys.exit( 0 )
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        analog = tr.read_sensor() 
        time.sleep(0.2)
    pass
pass