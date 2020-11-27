# coding: utf-8
from gpiozero import TrafficLights
from time import sleep

trafficLights = TrafficLights(2, 3, 4)

lights = [ trafficLights.green, trafficLights.amber, trafficLights.red ]
durations = [ 3, 2, 5 ]
frequecies = [ 0, 2, 0 ]

light_no = 0 

while True :
   for light in lights :
      light.off()
   pass

   light_no = light_no % 3 

   light = lights[ light_no ]

   light.on()

   duration = durations[ light_no ]

   sleep(duration) 

   light_no += 1 
pass
