# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import inspect, numpy as np, logging as log

from Config import  cfg
from time import sleep, time
from LineSensor import LineSensor

log.basicConfig(
    format='%(asctime)s, %(levelname)s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

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

        global line_sensor_running
        line_sensor_running = False
    pass

    import signal
    signal.signal(signal.SIGINT, signal_handler)

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    mpl.rcParams['toolbar'] = 'None'
    
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
    fig = plt.figure( "Line Sensor", figsize=(12, 6) )
    fig.canvas.mpl_connect('close_event', on_plot_close)

    ax = fig.add_subplot(111)

    sensors = [ [], [], [], [], [] ]
    data = [ [], {} ]
    len_sensors = len( sensors )
    colors = [ ( c/len_sensors, c/len_sensors, c/len_sensors ) for c in range( len_sensors ) ][::-1]
            
    interval = 0.01
    max_len = 6
    max_count = 0 

    idx = 0 

    def format_xaxis( t, pos=None ) :
        if t == -1 :
            return 0

        t = t + idx
        ti = int( t )
        return ti if ti == t else t
    pass

    while line_sensor_running :
        pos, norm, sum_norm, sensor, check_time = lineSensor.read_sensor() 

        if do_plot_chart == False :
            sleep( interval )
            continue
        pass

        if len( sensors[0] ) > max_len :
            for s in sensors :
                s.pop( 0 )
            pass
        pass

        # append norma data
        for i, s in enumerate( sensor ) :
            sensors[i].append( s )

            d = data[1]
            if s not in d :
                d[s] = 1
                data[0].append( -1 )
            else :
                t = d[s] = d[s] + 1
                if d[s] > max_count :
                    max_count = d[s]
            pass
        pass
        
        ax.clear()

        # plot norm sensor data
        x = np.arange( len(sensors[0]))
        for i, s in enumerate( sensors ):
            rect = ax.bar( x + (i-2)/6, s, color=colors[i], width=1/6, label=f's{i}' )
            ax.bar_label( rect, padding=3, fontsize='small')
        pass

        if 1 : 
            s = np.array( list(data[1].values()) )
            ax.scatter( data[0], data[1].keys(), s=s, label='data', color='darkorange' )
        pass

        ax.xaxis.set_major_formatter( format_xaxis )
        ax.set_xlim( -1.5, max_len + 0.5 )
        ax.set_ylim( 0, 800 )
        ax.legend(title='', ncol=7, fontsize='small' )
        ax.set_title( "Line Sensor Range\n" )
        ax.set_ylabel( "Sensor" )
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

        idx += 1 
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