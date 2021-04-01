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

            text = f""

            if idx == 0 :
                hostname = os.popen("hostname").read().split()[0]
        
                text = f"{hostname}"
            if idx == 1 :
                ipaddr = os.popen("hostname -I").read().split()[0]
        
                text = f"{ipaddr}"
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

            # text width
            tw = font.getsize(text)[0]

            # text center align
            x = (w - tw)//2
            
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