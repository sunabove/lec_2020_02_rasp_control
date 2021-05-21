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
    fig = plt.figure( "Line Sensor", figsize=(8, 6) )
    fig.canvas.mpl_connect('close_event', on_plot_close)

    ax = fig.add_subplot(111)

    times = [] # times
    sensors = [ [], [], [], [], [] ]
    
    bottom = -4
    interval = 0.01

    idx = 0 

    while line_sensor_running :
        pos, norm, sum_norm, sensor, check_time = lineSensor.read_sensor() 

        if do_plot_chart == False :
            sleep( interval )
            continue
        pass

        if len( times ) > 16 :
            times.pop( 0 ) 

            for s in sensors :
                s.pop( 0 )
            pass
        pass

        # append time data
        times.append( check_time )

        # append norma data
        for i, s in enumerate( sensor ) :
            sensors[i].append( s )
        pass
        
        ax.clear()

        # plot norm sensor data
        for i, s in enumerate( sensors ):
            ax.bar( np.array(times) + interval*i/6, s, width=0.35 )
        pass

        #ax.set_ylim( -4.8, 3.2 )
        ax.xaxis.set_major_formatter( format_date )
        ax.legend(title='', loc='lower center', fontsize='small' )
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