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
# 辞書をリストで持たせる。[['開始時刻', '終了時刻'], ['開始時刻', '終了時刻'], ['開始時刻', '終了時刻'], ...]
list_dict_mtg = [{'start_time': datetime.time(10, 0), 'end_time': datetime.time(11, 0)}, {'start_time': datetime.time(13, 0), 'end_time': datetime.time(14, 0)}, {'start_time': datetime.time(15, 0), 'end_time': datetime.time(16, 30)}]

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

        # 2重のリストに変換
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

    # 開始時間到来前のMTG一覧の取得（表示可能な最大MTG数は6件）
    for i in list_mtg_schedule[:6]:
        if i['status'] != 2:
            # list_notfinishedのリスト1つ分の中身は、['10:00 - 11:00', 0]になるイメージ
            list_notfinished.append([i['start_time'].strftime('%H:%M') + ' - ' + i['end_time'].strftime('%H:%M'), i['status']])

    # 6件分の描画を行うため、MTG数が6件に満たない場合は空欄を入れる
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
            # drawredが赤枠表示の意味
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
#list_dict_mtg = get_schedule_list()
for h in list_dict_mtg:
    # 各MTGのリストにステータスを代入（0: MTG前, 1: MTG中, 2: MTG終了）
    h['status'] = 0

#print(list_dict_mtg)


# MTGステータスの合計値を初期値として格納
sum_status = sum([j['status'] for j in list_dict_mtg])
# 電子ペーパーの描画
draw_schedule(list_dict_mtg)

# 実際に動かすところ。大きく2つに分かれ、①MTGステータス更新があるか確認、②MTGステータスがある場合、電子ペーパーに描画する。
# 30秒おきにループさせ、さらに時間順に並んだMTGリストの中から、開始時間をすぎかつ終了時間までのMTGがあれば赤枠を描画し、終了時間が過ぎれば一覧を表示する
while True:
    # 各MTGをループで回し、全MTGについてステータス更新があるか確認
    for i in list_dict_mtg:
        current_time = datetime.datetime.now().time()
        # MTG開始3分前からMTG中と表示するようにする
        start_time = (datetime.datetime.combine(datetime.date.today(), i['start_time']) - datetime.timedelta(minutes=3)).time()
        end_time = i['end_time']
        if i['status'] == 1:
            # ステータス1で終了時刻になったら、ステータスを2に変更
            if end_time < current_time:
                print('MTG終わったね')
                print('MTG一覧を表示するようにするよ。')
                i['status'] = 2
                print(i)
                print(list_dict_mtg)
            else:
                print('すでにMTG中と表示されてるね。')
                print(i)
        # 開始時刻を過ぎ、終了時間前のMTGについて、ステータスを1に変更
        elif start_time < current_time and current_time < end_time:
            print('始まるよ')
            print('電子ペーパーでMTG中って表示するよ。')
            i['status'] = 1
            print(i)
            print(list_dict_mtg)
        elif current_time < start_time:
            print('まだ始まってないよ')
            print(i)
        else:
            print('もう終わったよ')
            i['status'] = 2
            print(i)

    # MTGステータスの合計値が前回から変更されている場合のみ、電子ペーパーに描画
    if sum_status != sum([j['status'] for j in list_dict_mtg]):
        # 電子ペーパーに描画
        draw_schedule(list_dict_mtg)
        # MTGステータス合計値の更新
        sum_status = sum([j['status'] for j in list_dict_mtg])

    time.sleep(30)
    print('')

