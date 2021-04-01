#!/usr/bin/python
# -*- coding:utf-8 -*-

import SSD1306
import time, traceback, os, socket
import psutil, shutil

from PIL import Image, ImageDraw, ImageFont

def service() :
    try:
        show = SSD1306.SSD1306()

        # Initialize library.
        show.Init()
        show.ClearBlack()

        gw = os.popen("ip -4 route show default").read().split()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((gw[2], 0))
        ipaddr = s.getsockname()[0]
        gateway = gw[2]
        hostname = socket.gethostname()
        print ("IP:", ipaddr, " GW:", gateway, " Hostname:", hostname)
            
        w = show.width
        h = show.height
        x = 20
        y = 4
        font = ImageFont.truetype('Font.ttf',15)
        # Create blank image for drawing.
        image1 = Image.new('1', [w, h], "WHITE")
        draw = ImageDraw.Draw(image1)
        
        def display_oled_info( idx = 0 ) :
            idx = idx % 5

            text = f"{hostname}"

            if idx == 0 :
                text = f"{ipaddr}"
            elif idx == 1 :
                text = f"{hostname}"
            elif idx == 2 :
                # Disk usage

                total, used, free = shutil.disk_usage("/")
                total //= (2**30)
                used //= (2**30)
                free //= (2**30)
                pct = used*100/total

                text = f"Disk : {pct:02.1f} %"
            elif idx == 3 :
                # CPU
                pct = psutil.cpu_percent()

                text = f"CPU : {pct:02.1f} %"
            elif idx == 4 :
                # RAM
                pct = psutil.virtual_memory()[2] 

                text = f"RAM : {pct:02.1f} %"
            pass

            print( f"text = {text}")
            
            draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 0)            
            draw.text( [x, y], text, font = font, fill = 0) 
            
            show.ShowImage(show.getbuffer(image1))
            
            time.sleep(2)

            print ("Turn off screen to prevent heating oled.")
            show.ClearBlack()

            time.sleep(1)
        pass

        idx = 0
        while True :
            display_oled_info(idx = idx) 
            idx += 1
        pass

    except IOError as e:
        print(e)    
    except KeyboardInterrupt:    
        print("ctrl + c:")
    finally:
        print( "Clear Black" )
        show.ClearBlack()
        show.Closebus()
    pass
pass

if __name__ == '__main__':
    service()
pass