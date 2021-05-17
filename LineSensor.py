# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import inspect, numpy as np, logging as log

from Config import  cfg
from time import sleep, time

log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class LineSensor :

    CS = 5
    Clock = 25
    Address = 24 
    DataOut = 23
    Button = 7

    def __init__(self, signal_range=cfg("signal_range", [240, 540]), num_sensors = 5, debug=0):
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

    def read_sensor(self, sum_norm_min = 0.09) : 
        debug = self.debug

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

            print()
            print( f"[{idx:05}] Sensor [ {sensor_text}  ] time = {check_time%60:.4f}(s)" )
            print( f"[{idx:05}] Normal [ {norm_text}  ] sum  = {sum_norm:.2g}" )
            print( f"[{idx:05}] Line   [ {road_text} ] pos  = {pos:.2g}" )
        pass

        return pos, norm, sum_norm, check_time
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

line_sensor_running = False
do_plot_chart = False

def service(debug=0) :
    debug and print("TRSensor")

    GPIO.setwarnings(False)
    GPIO.cleanup()

    global line_sensor_running, do_plot_chart
    line_sensor_running = True

    lineSensor = LineSensor(debug=debug)

    def signal_handler(signal, frame):
        print("", flush=True) 
        
        print('You have pressed Ctrl-C.')

        line_sensor_running = False
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    mpl.rcParams['toolbar'] = 'None'
    
    times = [] # times
    # signal charts
    xys = [ [ [], [] ], [ [], [] ], [ [], [] ], [ [], [] ], [ [], [] ], ]
    position = [] # position
    min_signal = [] # minimal signal

    def format_date( t, pos=None ) :
        t = t%60
        return int(t)
    pass

    do_plot_chart = True

    def on_plot_close(event):
        print('Closed Figure!')
        global line_sensor_running
        global do_plot_chart
        do_plot_chart = False
        line_sensor_running = False
    pass
    
    plt.style.use('seaborn-whitegrid')
    fig = plt.figure( "Line Sensor", figsize=(8, 6) )
    fig.canvas.mpl_connect('close_event', on_plot_close)

    ax = fig.add_subplot(111)
    
    if 0 :
        ax.scatter( xys[0][0], xys[0][1], marker='s' ) 

        fig.show()
        fig.canvas.draw()
    pass

    bottom = -4

    interval = 0.01
    while line_sensor_running :
        pos, norm, sum_norm, check_time = lineSensor.read_sensor() 

        if do_plot_chart == False :
            sleep( interval )
            continue
        pass

        if len( times ) > 16 :
            x0 = times[0]
            times.pop( 0 )
            position.pop( 0 )
            min_signal.pop( 0 )

            for xy in xys :
                remove_cnt = 0 
                x = xy[0]
                y = xy[1]
                while x and x0 == x[0] :
                    x.pop( 0 )
                    y.pop( 0 )
                pass
            pass
        pass

        # append time data
        times.append( check_time )

        # append norma data
        for i, n in enumerate( norm ) :
            idx = int( n*4 + 0.5 )
            xys[idx][0].append( check_time )
            xys[idx][1].append( i - 2 )
        pass

        signal = sum_norm/5
        # append pos data
        position.append( pos )
        min_signal.append( signal + bottom  )
        
        ax.clear()

        # plot norm sensor data
        for i, xy in enumerate( xys ):
            n = (i+1)/5
            ax.scatter( xy[0], xy[1], marker='s', label=f'{n}' )
        pass

        # plot pos data
        ax.plot( times, position, 'g', label='position' )
        ax.plot( times, min_signal, 'r', label='signal strength' )
        
        for x, y in zip( times, min_signal ) :
            label = f"{(y + 4)*5:.2f}"
            ax.annotate(label, (x,y), textcoords="offset points", xytext=(0,10),ha='center')
        pass

        ax.set_ylim( -4.8, 3.2 )
        ax.xaxis.set_major_formatter( format_date )
        ax.legend(title='', ncol=7, loc='lower center', fontsize='small' )
        ax.set_title( "Line Sensor\n" )
        ax.set_ylabel( "Position" )
        ax.set_xlabel( "Time (s)" )

        if do_plot_chart :
            try : 
                plt.tight_layout()
                fig.canvas.draw()
                plt.pause( interval )
            except :
                do_plot_chart = False
                line_sensor_running = False
            pass
        pass
    pass

    lineSensor.finish()
    sleep( 0.5 )

    print( "Good bye!")
pass # -- service

def stop():
    line_sensor_running = False 
pass

if __name__ == '__main__':
    service( debug = 1 )
pass