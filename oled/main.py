import sys
from os import path
sys.path.append( path.dirname(path.realpath(__file__)) )

from SSD1306 import SSD1306 
from time import sleep 
import traceback, os, socket
import psutil, shutil, numpy as np

from PIL import Image, ImageOps, ImageDraw, ImageFont

def service() :
    try:
        show = SSD1306()

        # Initialize library.
        show.Init()
        show.ClearBlack()

        w = show.width
        h = show.height

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
            idx = idx % 6

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
            elif idx == 5 :
                # show image by scrolling up by n pixel
                for y in range( 0, lena.size[1], 4 ) :
                    im = Image.new('1', (w, h), 0 ) # create a new blank image
                    im_draw = ImageDraw.Draw( im )
                    im_draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 1)
                    
                    y2 = y + h 
                    if y2 > lena.size[1] :
                        y2 = lena.size[1]
                    pass
                    
                    crop = lena.crop( [0, y, w, y2 ] )

                    im.paste( crop, box=[0, 0, w, y2 - y ] ) 
                    
                    show.ShowImage( show.getbuffer( im ) )
                    sleep( 0.001 )
                pass
            pass

            print( f"text = {text}")

            # text width
            tw = font.getsize(text)[0]

            # text center align
            x = (w - tw)//2
            y = 4
            
            draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 0)
            draw.text( [x, y], text, font = font, fill = 0) 
            
            show.ShowImage( show.getbuffer(image) )

            sleep(2)

            print ("Turn off screen to prevent heating oled.")
            show.ClearBlack()

            sleep(1)
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