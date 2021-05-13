# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import inspect, numpy as np, logging as log

from time import sleep, time

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

    def __init__(self, signal_range=[240, 540], num_sensors = 5, debug=0):
        self.debug = debug

        self.signal_range = signal_range
        self.white_signal = max( signal_range )
        self.black_signal = min( signal_range )

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

        for s in range( num_sensors + 1 ):
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

            sleep(0.0001)
            GPIO.output(cs, GPIO.HIGH)
        pass

        return np.array( value[1:] ), time()
    pass # -- read_analog

    def calibrate(self):
        num_sensors = self.num_sensors

        max_sensor_values = [0]*num_sensors
        min_sensor_values = [0]*num_sensors

        for j in range(0,10):
        
            sensor_values, check_time = self.read_analog();
            
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
        sensor_values, check_time = self.read_analog();

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

    def read_sensor(self, sum_norm_min = 0.09, debug=None) : 
        if debug is None:
            debug = self.debug
        pass

        self.idx += 1

        idx = self.idx
        
        # 신호 읽기
        sensor, check_time = self.read_analog()

        # 신호 위치
        white_signal = self.white_signal
        black_signal = self.black_signal

        # 신호 정규화
        norm = self.normalize( sensor, white_signal, black_signal )
        pos = 0.0

        sum_norm = sum( norm )

        if sum_norm > sum_norm_min :
            # sum_norm_min 이상의 신호일 때만, 라인위의 위치를 감지한다.
            for i, n in enumerate( norm ) :
                pos += (i+1)*n
            pass

            pos = pos/sum_norm

            pos = pos - 3.0
        else :
            # sum_norm_min 이하이면, 라인위에 있지 않은 것으로 간주한다.
            pos = -3 if self.prev_pos < 0 else 3 
        pass

        self.prev_pos = pos

        if debug : 
            sensor_text = ", ".join( [ f"{x:4}" for x in sensor ] )
            norm_text = ", ".join( [ f"{x:.2f}" for x in norm ] )
            road_text = self.to_sensors_text( norm, 5 )
        
            print( f"[{idx:04}] Sensor [ {sensor_text}  ] " )
            print( f"[{idx:04}] Normal [ {norm_text}  ] sum = {sum_norm:.2g}" )
            print( f"[{idx:04}] Line   [ {road_text} ] pos = {pos:.2g}" )
            print()
        pass

        return pos, norm, check_time
    pass # -- read_sensor

    def normalize(self, sensor, white_signal, black_signal) :
        # 신호 위치
        pos = 0
        
        # normalize
        norm = np.zeros( len( sensor ), np.float32 )
        wb_diff = white_signal - black_signal

        for i, s in enumerate( sensor ):
            n = 0
            if s < black_signal :
                n = 1 
            elif s > white_signal :
                n = 0
            else :
                n = (white_signal - s)/wb_diff
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

    GPIO.setwarnings(False)
    GPIO.cleanup()

    running = True

    tr = TRSensor()

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        print('You have pressed Ctrl-C.')

        global running
        running = False
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    mpl.rcParams['toolbar'] = 'None'
    
    x = []
    y = []

    def format_date( t, pos=None ) :
        t = t%60
        return int(t)
    pass

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.scatter( x, y, marker='s' )

    fig.show()
    fig.canvas.draw()

    interval = 0.01
    while running :
        pos, norm, check_time = tr.read_sensor( debug=1 ) 

        if len( x ) > 20 :
            x.pop( 0 )
            y.pop( 0 )
        pass

        x.append( check_time )
        y.append( pos )
        
        ax.clear()
        ax.scatter( x, y, marker='s' )
        ax.plot( x, y )

        ax.set_ylim( -3.5, 3.5 )
        ax.xaxis.set_major_formatter( format_date )
        fig.canvas.draw()

        plt.pause( interval )
    pass

    tr.finish()
    sleep( 0.5 )

    print( "Good bye!")
pass