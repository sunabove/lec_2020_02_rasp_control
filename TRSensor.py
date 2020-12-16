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

    def __init__(self, num_sensors = 5, white=450, black = 370):
        self.white = white
        self.black = black
        self.num_sensors = num_sensors
        self.idx = 0 

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
    pass

    def __del__(self):
        self.finish()
    pass

    def finish(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for port in [ self.Clock, self.Address, self.CS, self.DataOut, self.Button ] :             
            GPIO.cleanup(port)
        pass
    pass
        
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

        return np.array( value[1:] )
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
    pass

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
    pass
            
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
    pass

    def read_sensors(self) : 
        self.idx += 1
        idx = self.idx
        white = self.white
        black = self.black

        sensors = self.read_analog()

        if np.all( sensors > white ) :
            log.info( f"[STOP] : All White {sensors}" )
        elif np.all( sensors < black ) :
            log.info( f"[FORE] : All Black {sensors}" )
        else :
            log.info( f"[MIX ] : Mixed     {sensors}" )
        pass

        return sensors
    pass

pass

# Simple example prints accel/mag data once per second:
if __name__ == '__main__':
    log.info("TRSensor")

    tr = TRSensor(white=450, black = 370)

    def exit( result ) :
        tr.finish()
        sleep( 0.5 )  
    pass

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        log.info('You have pressed Ctrl-C.')

        exit( 0 )

        log.info( "Goood bye!")

        import sys
        sys.exit( 0 )
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        analog = tr.read_sensors() 
        time.sleep(0.2)
    pass

pass