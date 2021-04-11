# coding: utf-8
from gpiozero import TrafficLights, Button
from time import sleep, time

tr = TrafficLights(23, 24, 25)

# 신호등 
lights = [ tr.green, tr.amber, tr.red ]
durations   = [ 5, 3, 10 ]   # 신호등을 켜는 시간 
periods     = [ 0, 1/3, 1/4 ]   # 깜빡이는 주기 

light_no = 0  # 현재 신호등 번호 
signal_no = 0 # 신호 번호 

# 신호 바꾸는 함수 
def change_signal() :
   print( "Button pressed." )
   global light_no, signal_no
   signal_no += 1 # 신호 번호를 하나 증가 시키고 
   light_no += 1  # 다음 신호등으로 변경한다.
pass

button = Button(17) # 버튼
button.when_pressed = change_signal  # 버튼을 누르면 신호를 변경한다.

while True :
   for light in lights :
      light.off()
   pass

   light_no = light_no % 3 

   curr_signal_no = signal_no # 현재 신호 번호 

   light = lights[ light_no ]

   duration = durations[ light_no ]  # 점등 시간
   period = periods[ light_no ]  # 깜빡이는 주기

   then = time() # 신호 시작 시각 
   elapsed = time() - then # 신호 노출 시간 

   # 신호 번호가 바뀌지 않고, 점듬 시간 이하 일 때, 신호를 깜빡인다.
   while ( curr_signal_no == signal_no ) and ( elapsed < duration ):
      period_no = 0
      
      if period > 0 :
         # 깜빡임 여부 설정 
         period_no = int( elapsed/period ) 
      pass
      
      # 신호 깜빡이기
      if period_no % 2 :
         light.off()
      else :
         light.on()
      pass

      if curr_signal_no == signal_no :
         sleep( 0.2 ) # 0.1 초 동안 멈춤.
         elapsed = time() - then # 신호 노출 시간 
      pass
   pass

   if curr_signal_no == signal_no : 
      # 현재 신호 횟수가 바뀌지 않았으면, 다음 신호를 점등한다.
      light_no += 1 
   pass
pass
