#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7b
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in7b Demo")
    
    epd = epd2in7b.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    #time.sleep(1)
    
    # Drawing on the image
    logging.info("Drawing")
    blackimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    redimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)

    # Drawing on the Vertical image
    logging.info("2.Drawing on the Vertical image...")
    LBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
    LRedimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
    drawblack = ImageDraw.Draw(LBlackimage)
    drawred = ImageDraw.Draw(LRedimage)
    
    drawred.rectangle((0, 0, 176, 12), fill = 0) # 上の枠
    drawred.rectangle((0, 0, 12, 264), fill = 0) # 左の枠
    drawred.rectangle((0, 252, 176, 264), fill = 0) # 下の枠
    drawred.rectangle((164, 0, 176, 264), fill = 0) # 右の枠
    drawblack.text((20, 15), 'Today\'s MTG', font = font24, fill = 0)
    drawblack.line((15, 48, 161, 48), fill = 0)
    drawred.text((20, 60), '09:00 - 10:00', font = font24, fill = 0)
    drawblack.text((20, 90), '10:00 - 11:00', font = font24, fill = 0)
    drawblack.text((20, 120), '11:00 - 12:00', font = font24, fill = 0)
    drawblack.text((20, 150), '13:00 - 14:00', font = font24, fill = 0)
    drawblack.text((20, 180), '14:00 - 15:00', font = font24, fill = 0)
    drawblack.text((20, 210), '', font = font24, fill = 0)
    epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRedimage))
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in7b.epdconfig.module_exit()
    exit()
