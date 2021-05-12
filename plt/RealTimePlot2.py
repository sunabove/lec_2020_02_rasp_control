# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
from random import randrange

x_data, y_data = [], []

figure = plt.figure()
line, = plt.plot_date(x_data, y_data, '-')

def init():
    return line,
pass

def update(frame):
    x_data.append(datetime.now())
    y_data.append(randrange(0, 100))
    
    line.set_data(x_data, y_data)
    
    figure.gca().relim()
    figure.gca().autoscale_view()

    return line,
pass

animation = FuncAnimation(figure, update, init_func=init, blit=1, interval=200)

plt.show()