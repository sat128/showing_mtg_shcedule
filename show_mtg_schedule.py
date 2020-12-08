#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime
import time
import sys
import os
import glob
import re
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7b
from PIL import Image,ImageDraw,ImageFont
import traceback


# データのイメージ
# リストでもたせる。[['開始時刻', '終了時刻'], ['開始時刻', '終了時刻'], ['開始時刻', '終了時刻'], ...]
#list_dict_mtg = [{'start_time': '11:00', 'end_time': '12:00'}, {'start_time': '13:00', 'end_time': '13:30'}, {'start_time': '15:00', 'end_time': '16:00'}]

################# `.ics`を読み込んでMTG時間を取得 ################
def get_schedule_list():
    path = '/home/pi/public/mtg_schedule/'

    list_ics = glob.glob(path + '*.ics')

    list_mtg_schedule = []

    # フォルダ内の`*.ics`ファイルから、開始時刻・終了時刻を取得し、リストに格納する。
    for i in list_ics:
        with open(i, encoding='utf_8') as f:
            s = f.readlines()
        
        # ファイル内のDTSTARTを取得。中身のイメージ→['DTSTART:20201028T060000Z\n']
        dtstart = [j for j in s if 'DTSTART' in j]
        # ファイル内のDTENDを取得
        dtend = [k for k in s if 'DTEND' in k]
        
        # TとZの間に挟まれた数字を上から4桁取得
        start_hhmm = re.findall('T(\d{6})Z', dtstart[0])[0][0:4]
        end_hhmm = re.findall('T(\d{6})Z', dtend[0])[0][0:4]

        # time型に変換し、UTCから9時間足して日本時間に変更
        start_hhmm = (datetime.datetime.strptime(start_hhmm, '%H%M') + datetime.timedelta(hours=9)).time()
        end_hhmm = (datetime.datetime.strptime(end_hhmm, '%H%M') + datetime.timedelta(hours=9)).time()

        # 2重のリストにい変換
        list_mtg_schedule.append([start_hhmm, end_hhmm])

    # リストを並べ替え
    list_mtg_schedule.sort()

    # 辞書を入れるためのリストを作成
    list_dict_mtg = []

    # MTGスケジュールを辞書型に変換
    for l in list_mtg_schedule:
        dict_schedule = {}
        dict_schedule['start_time'] = l[0]
        dict_schedule['end_time'] = l[1]
        list_dict_mtg.append(dict_schedule)

    return list_dict_mtg


################# MTG一覧表示関数定義 ################
def draw_schedule(list_mtg_schedule):
    list_notfinished = []

    # 終了済みMTGの削除
    for i in list_mtg_schedule[:5]:
        if i['status'] != 2:
            list_notfinished.append([i['start_time'].strftime('%H:%M') + ' - ' +i['end_time'].strftime('%H:%M'), i['status']])

    for j in range(6 - len(list_notfinished)):
        list_notfinished.append(['', ''])

    # 一番直近のMTG statusが「1」(on going)の場合は、赤枠付きで表示。無ければモノクロ表示。
    if list_notfinished[0][1] == 1:
        try:
            epd = epd2in7b.EPD()
            epd.init()
            #epd.Clear()
            #time.sleep(1)
            
            # Drawing on the image
            blackimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
            redimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
            
            font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        
            # Drawing on the Vertical image
            LBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
            LRedimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
            drawblack = ImageDraw.Draw(LBlackimage)
            drawred = ImageDraw.Draw(LRedimage)
            
            drawred.rectangle((0, 0, 176, 12), fill = 0) # 上の枠
            drawred.rectangle((0, 0, 12, 264), fill = 0) # 左の枠
            drawred.rectangle((0, 252, 176, 264), fill = 0) # 下の枠
            drawred.rectangle((164, 0, 176, 264), fill = 0) # 右の枠
            drawred.text((20, 15), 'MTG ongoin\'', font = font24, fill = 0)
            drawblack.line((15, 48, 161, 48), fill = 0)
            drawred.text((20, 60), list_notfinished[0][0], font = font24, fill = 0)
            drawblack.text((20, 90), list_notfinished[1][0], font = font24, fill = 0)
            drawblack.text((20, 120), list_notfinished[2][0], font = font24, fill = 0)
            drawblack.text((20, 150), list_notfinished[3][0], font = font24, fill = 0)
            drawblack.text((20, 180), list_notfinished[4][0], font = font24, fill = 0)
            drawblack.text((20, 210), list_notfinished[5][0], font = font24, fill = 0)
            epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRedimage))
            
        except IOError as e:
            logging.info(e)
            
        except KeyboardInterrupt:    
            logging.info("ctrl + c:")
            epd2in7b.epdconfig.module_exit()
            exit()
    else:
        try:
            epd = epd2in7b.EPD()
            epd.init()
            #epd.Clear()
            #time.sleep(1)
            
            # Drawing on the image
            blackimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
            redimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
            
            font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        
            # Drawing on the Vertical image
            LBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
            LRedimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
            drawblack = ImageDraw.Draw(LBlackimage)
            drawred = ImageDraw.Draw(LRedimage)
            
            drawblack.text((20, 15), 'Today\'s MTG', font = font24, fill = 0)
            drawblack.line((15, 48, 161, 48), fill = 0)
            drawblack.text((20, 60), list_notfinished[0][0], font = font24, fill = 0)
            drawblack.text((20, 90), list_notfinished[1][0], font = font24, fill = 0)
            drawblack.text((20, 120), list_notfinished[2][0], font = font24, fill = 0)
            drawblack.text((20, 150), list_notfinished[3][0], font = font24, fill = 0)
            drawblack.text((20, 180), list_notfinished[4][0], font = font24, fill = 0)
            drawblack.text((20, 210), list_notfinished[5][0], font = font24, fill = 0)
            epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRedimage))
            
        except IOError as e:
            logging.info(e)
            
        except KeyboardInterrupt:    
            logging.info("ctrl + c:")
            epd2in7b.epdconfig.module_exit()
            exit()

################# MTG一覧表示関数の実行 ################

# MTG一覧の取得
list_dict_mtg = get_schedule_list()
for h in list_dict_mtg:
    h['status'] = 0

print(list_dict_mtg)


# MTGステータスの初期値を格納
sum_status = sum([j['status'] for j in list_dict_mtg])
draw_schedule(list_dict_mtg)

# 実際に動かすところ
while True:
    # ファイルを毎回とってくる

    # 終了時刻が過ぎていないものをとってくる
    i = []
    for i in list_dict_mtg:
        current_time = datetime.datetime.now().time()
        start_time = (datetime.datetime.combine(datetime.date.today(), i['start_time']) - datetime.timedelta(minutes=3)).time()
        end_time = i['end_time']
        if i['status'] == 1:
            # ステータス1でも終了時刻になったら、ステータス更新。MTG一覧表示に変更
            if end_time < current_time:
                print('MTG終わったね')
                print('MTG一覧を表示するようにするよ。')
                i['status'] = 2
                print(i)
                print(list_dict_mtg)
                ################# MTG一覧表示関数の実行 ################
                #draw_schedule(list_mtg)
            else:
                print('すでにMTG中と表示されてるね。')
                print(i)

        elif start_time < current_time and current_time < end_time:
            print('始まるよ')
            print('電子ペーパーでMTG中って表示するよ。')
            i['status'] = 1
            print(i)
            print(list_dict_mtg)
            ################# MTG中！！って表示する関数の実行 ################
            #draw_schedule(list_mtg)
        elif current_time < start_time:
            print('まだ始まってないよ')
            print(i)

        else:
            print('もう終わったよ')
            i['status'] = 2
            print(i)

    # MTGステータスが前回から変更されている場合のみ、電子ペーパーに描画
    if sum_status != sum([j['status'] for j in list_dict_mtg]):
        # 電子ペーパーに描画
        draw_schedule(list_dict_mtg)
        # MTGステータスの更新
        sum_status = sum([j['status'] for j in list_dict_mtg])

    time.sleep(30)
    print('')

