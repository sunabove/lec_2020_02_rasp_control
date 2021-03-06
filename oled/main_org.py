﻿#!/usr/bin/python
# -*- coding:utf-8 -*-

import SSD1306
import time
import traceback

from PIL import Image,ImageDraw,ImageFont

time_bitmap = [
0x00,0x06,0x0A,0xFE,0x0A,0xE6,0x00,0xF0,0x00,0xF8,0x00,0xFC,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x84,0x48,0xFE,0x32,0xB4,0x48,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFE,0x06,0x0A,0x12,0x12,0x12,0x12,
0x12,0x0A,0x06,0xFE,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x86,0x02,0x78,0x84,0xA4,0x68,0x02,0x86,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0E,0x7A,0x86,0x84,0xB4,0xA4,0xA6,0x7A,0x0E,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x78,0x48,
0xFE,0x82,0xBA,0xBA,0x82,0xBA,0xBA,0x82,0xBA,0xBA,0x82,0xBA,0xBA,0x82,0xFE,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x01,0x00,0x00,0x00,0x00,0x00,
0xE0,0xF0,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x31,0x31,0xF1,0xE1,0x01,0x01,0xE1,
0xF1,0x31,0x31,0x31,0x30,0x30,0x30,0x30,0x30,0x30,0xF0,0xE0,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x01,0x01,0x30,0x30,0x30,0x30,0x31,0x31,0x30,0x30,0x30,0x30,0x30,
0xF0,0xF0,0x00,0x00,0x30,0x30,0x30,0x30,0x31,0x31,0x30,0x30,0x30,0x31,0x31,0xF0,
0xF0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x40,0xC0,0xC0,0x00,0xC0,0xC0,0x40,0x00,0x40,0xC0,0x40,0x40,0xC0,0x00,0x40,0xC0,
0x00,0x00,0xC0,0x40,0x00,0x40,0xC0,0x00,0x00,0xC0,0x40,0x00,0x00,0x00,0x00,0x00,
0xFF,0xFF,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF,0x00,0x00,0xFF,
0xFF,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0xFF,0xFF,0x00,0x00,0x00,0x0E,
0x0E,0x0E,0x00,0x00,0x00,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,
0xFF,0xFF,0x00,0x00,0xE0,0xE0,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x7F,
0x7F,0x00,0x00,0x00,0x00,0x00,0x80,0x80,0x00,0x00,0x80,0x80,0x00,0x00,0x80,0x80,
0x80,0x00,0x00,0x80,0x80,0x80,0x00,0x80,0x80,0x80,0x00,0x80,0x80,0x80,0x80,0x80,
0x20,0x3F,0x03,0x3C,0x03,0x3F,0x20,0x00,0x20,0x3F,0x22,0x27,0x30,0x00,0x20,0x3F,
0x03,0x0C,0x3F,0x20,0x00,0x00,0x1F,0x20,0x20,0x1F,0x00,0x00,0x00,0x00,0x00,0x00,
0x3F,0x7F,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x7F,0x3F,0x00,0x00,0x3F,
0x7F,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x7F,0x3F,0x00,0x00,0x00,0x07,
0x07,0x07,0x00,0x00,0x00,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,
0x7F,0x7F,0x00,0x00,0x7F,0x7F,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x60,
0x60,0x00,0x00,0x00,0x00,0x00,0x40,0x7F,0x04,0x04,0x7F,0x40,0x00,0x3F,0x40,0x40,
0x40,0x3F,0x00,0x40,0x7F,0x07,0x78,0x07,0x7F,0x40,0x00,0x40,0x7F,0x44,0x4E,0x61
]

try:    
    show = SSD1306.SSD1306()

    # Initialize library.
    show.Init()
    show.ClearBlack()

    print( len(time_bitmap), show.width, show.height )
    

    # Create blank image for drawing.
    image1 = Image.new('1', (show.width, show.height), "WHITE")
    draw = ImageDraw.Draw(image1)    
    draw.rectangle((0, 0, 127, 31), outline = 0)
    draw.text((20,0), 'wavehshare', font = ImageFont.truetype('Font.ttf',15), fill = 0)
    show.ShowImage(show.getbuffer(image1))
    time.sleep(2)

    print ("***draw image")
    show.ShowImage(time_bitmap)
    show.Closebus()

except IOError as e:
    show.Closebus()
    print(e)
    
except KeyboardInterrupt:    
    print("ctrl + c:")
    show.Closebus()
