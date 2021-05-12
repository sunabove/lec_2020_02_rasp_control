# coding: utf-8

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['toolbar'] = 'None'

#from IPython.display import display, clear_output

if False :
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    for i in range(20):
        x = np.arange(0, i, 0.1)
        y = np.sin(x)

        ax.set_xlim(0, i)

        ax.cla()
        ax.plot(x, y)

        plt.pause(0.5)
    pass
pass

if True :
    fig = plt.figure()
    fig.canvas.toolbar_visible = False

    ax = fig.add_subplot(1, 1, 1)

    for i in range(30):
        if i < 20 :
            ax.set_xlim(0, 20 )
        else :
            ax.set_xlim(0, i)
            
            ax.cla()
        pass       

        ax.plot(i, 1, marker='x')

        plt.pause(0.1)
    pass
pass

import signal
signal.pause()