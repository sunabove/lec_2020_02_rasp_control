# coding: utf-8
from gpiozero import TrafficLights
from time import sleep
from time import time

trafficLights = TrafficLights(2, 3, 4)

# 신호등 
lights = [ trafficLights.green, trafficLights.amber, trafficLights.red ]
durations = [ 3, 2, 5 ]   # 신호등을 켜는 시간 
periods = [ 0, 1/3, 1/4 ]   # 깜빡이는 주기 

light_no = 0  # 현재 신호등 번호 
signal_no = 0 # 신호 번호 

while True :
   for light in lights :
      light.off()
   pass

   light_no = light_no % 3 

   curr_signal_no = signal_no # 현재 신호 번호 

   light = lights[ light_no ]

   duration = durations[ light_no ]  # 점등 시간
   period = periods[ light_no ]  # 깜빡이는 주기

   then = time()
   elapsed = time() - then

   while elapsed < duration :      
      period_no = 0
      
      if period > 0 :
         # 깜빡임 여부 설정 
         period_no = int( elapsed/period ) 
      pass
      
      # 신호등 깜빡이기
      if period_no % 2 == 0 :
         light.on()
      else :
         light.off()
      pass

      sleep( 0.1 ) # 0.1 초 동안 멈춤.
      elapsed = time() - then
   pass

   if curr_signal_no == signal_no : 
      # 현재 신호 횟수가 바뀌지 않았으면, 다음 신호등을 점등한다.
      light_no += 1 
   pass
pass
