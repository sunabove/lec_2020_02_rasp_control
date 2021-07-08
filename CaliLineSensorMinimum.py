# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import inspect, numpy as np, logging as log

from Config import cfg
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
        pos, norm, sum_norm, sensor, check_time = lineSensor.read_sensor() 

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