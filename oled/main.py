import sys
from os import path
sys.path.append( path.dirname(path.realpath(__file__)) )

from SSD1306 import SSD1306 
from time import sleep 
import traceback, os, socket
import psutil, shutil, numpy as np

from PIL import Image, ImageOps, ImageDraw, ImageFont

oled_alive = True 

oled_disp = SSD1306()

def stop() :
    oled_alive = 0

    w = oled_disp.width
    h = oled_disp.height
    
    image = Image.new('1', [w, h], "WHITE")
    draw = ImageDraw.Draw(image)

    font_path = path.join( path.dirname(path.realpath(__file__)), 'Font.ttf' )
    font = ImageFont.truetype( font_path, 15)

    text = "SHUTDOWN"

    tw = font.getsize(text)[0]

    # text center align
    x = (w - tw)//2
    y = 4
    
    draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 0)
    draw.text( [x, y], text, font = font, fill = 0) 
    
    oled_disp.ShowImage( oled_disp.getbuffer(image) )

    oled_disp.Closebus()
pass # -- stop

pass # -- stop

def service() :
    try:
        global oled_alive

        oled_alive = True 

        # Initialize library.
        oled_disp.Init()
        oled_disp.ClearBlack()

        w = oled_disp.width
        h = oled_disp.height

        font_path = path.join( path.dirname(path.realpath(__file__)), 'Font.ttf' )
        print( f"font_path = {font_path}" )  
        font = ImageFont.truetype( font_path, 15)

        # open lena image
        img_path = path.join( path.dirname(path.realpath(__file__)), 'lena.png' )        
        print( f"img_path = {img_path}" )         
        lena = Image.open( img_path )

        if 1 : 
            im = lena
            # convert to grayscale
            im = ImageOps.grayscale(im)
            # rescale to show width height
            im = im.resize( [w, im.size[1]*w//im.size[0] ], Image.ANTIALIAS)
            #im = np.asarray(im)
            #im = im.ravel()

            #print( f"im.shape ={im.shape}" )

            lena = im
        pass

        print( f"lena shape={lena.size}" )
        
        # Create blank image for drawing.
        image = Image.new('1', [w, h], "WHITE")
        draw = ImageDraw.Draw(image)
        
        def display_oled_info( idx = 0 ) :
            if idx >= 0 : 
                idx = idx % 6
            pass

            text = f""

            if idx < 0 :
                text = "SHUTDOWN"
            elif idx == 0 :
                hostname = os.popen("hostname").read().strip().split()[0]
        
                text = f"{hostname}"
            if idx == 1 :
                ipaddr = os.popen("hostname -I").read().strip().split()[-1]
        
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
            elif idx == 5 :
                # show image by scrolling up by n pixel
                for y in range( 0, lena.size[1], 4 ) :
                    if not oled_alive :
                        break
                    pass

                    im = Image.new('1', (w, h), 0 ) # create a new blank image
                    im_draw = ImageDraw.Draw( im )
                    im_draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 1)
                    
                    y2 = y + h 
                    if y2 > lena.size[1] :
                        y2 = lena.size[1]
                    pass
                    
                    crop = lena.crop( [0, y, w, y2 ] )

                    im.paste( crop, box=[0, 0, w, y2 - y ] ) 
                    
                    oled_alive and oled_disp.ShowImage( oled_disp.getbuffer( im ) )
                    sleep( 0.001 )
                pass
            pass

            print( f"text = {text}")

            if text : 
                # text width
                tw = font.getsize(text)[0]

                # text center align
                x = (w - tw)//2
                y = 4
                
                draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 0)
                draw.text( [x, y], text, font = font, fill = 0) 
                
                oled_disp.ShowImage( oled_disp.getbuffer(image) )
            pass

            sleep(2)

            if idx >= 0 : 
                print ("Turn off screen to prevent heating oled.")
                oled_disp.ClearBlack()
            pass

            sleep(1)
        pass

        idx = 0
        while oled_alive :
            display_oled_info(idx = idx) 
            idx += 1

            idx %= 1000
        pass

        stop()

    except IOError as e:
        oled_disp.ClearBlack()

        print(e)    
    except KeyboardInterrupt:
        oled_disp.ClearBlack()

        print("ctrl + c:")
    finally:
        stop()
    pass
pass  # -- service

if __name__ == '__main__':
    service()
pass