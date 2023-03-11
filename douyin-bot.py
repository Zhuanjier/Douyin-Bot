# -*- coding: utf-8 -*-
import sys
import os
import json
import random
import time
from uuid import uuid1

from PIL import Image
import argparse

if sys.version_info.major != 3:
    print('Please run under Python3')
    exit(1)
try:
    from common import debug, config, screenshot, UnicodeStreamFilter
    from common.auto_adb import auto_adb
    from common import apiutil
    from common.compression import resize_image
except Exception as ex:
    print(ex)
    print('请将脚本放在项目根目录中运行')
    print('请检查项目根目录中的 common 文件夹是否存在')
    exit(1)

VERSION = "R_0.0.3"

DEBUG_SWITCH = True
FACE_PATH = 'face/'

adb = auto_adb()
adb.test_device()
config = config.open_accordant_config()

# 审美标准
BEAUTY_THRESHOLD = config['BEAUTY_THRESHOLD']
# 最小年龄
GIRL_MIN_AGE = config['GIRL_MIN_AGE']


# 生成一个随机偏移量
def _random_bias(num):
    return random.randint(-num, num)


# 检查是否已经关注过
def hasBeenFollowed(img):
    # 读取图片
    im = Image.open(img)
    # 获取图片的宽度和高度
    width, height = im.size
    # 获取图片的像素
    pix = im.load()
    # 获取当前像素的颜色
    color = pix[config['follow_bottom']['x'], config['follow_bottom']['y']]
    # 如果当前像素的rgba最后一个值为255，说明是关注按钮
    if color[0]>250 and color[1]>42 and color [1]<48 and color[2]>80 and color[2]<90 and color[3]>250:
        print('暂未关注过')
        return False
    print('已经关注过')
    return True


# 翻页
def next_page():
    cmd = 'shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=config['center_point']['x'],
        y1=config['center_point']['y'] + config['center_point']['ry'],
        x2=config['center_point']['x'],
        y2=config['center_point']['y'],
        duration=200
    )
    adb.run(cmd)
    time.sleep(1.5)


# 关注
def follow_user(way):
    if way == 0:
        return
    # 检查是否已经关注过
    if hasBeenFollowed('autojump.png'):
        return
    cmd = 'shell input tap {x} {y}'.format(
        x=config['follow_bottom']['x'] + _random_bias(10),
        y=config['follow_bottom']['y'] + _random_bias(10)
    )
    adb.run(cmd)
    time.sleep(0.5)


# 点赞
def thumbs_up(way):
    if way == 1:
        cmd = 'shell input tap {x} {y}'.format(
            x=config['star_bottom']['x'] + _random_bias(10),
            y=config['star_bottom']['y'] + _random_bias(10)
        )
        adb.run(cmd)
    elif way == 2:
        cmd = 'shell input tap {x} {y}'.format(
            x=config['center_point']['x'] + _random_bias(10),
            y=config['center_point']['y'] + _random_bias(10)
        )
        adb.run(cmd)
        adb.run(cmd)
    time.sleep(0.5)

# 点击
def tap(x, y):
    cmd = 'shell input tap {x} {y}'.format(
        x=x + _random_bias(10),
        y=y + _random_bias(10)
    )
    adb.run(cmd)

# 自动回复
def reply(way):
    if way == 0:
        return
    # msg = "垆边人似月，皓腕凝霜雪。就在刚刚，我的心动了一下，小姐姐你好可爱呀_Powered_By_Python"
    msg = config['comment_contain']
    # 点击右侧评论按钮
    tap(config['comment_bottom']['x'], config['comment_bottom']['y'])
    time.sleep(1)
    # 弹出评论列表后点击输入评论框
    tap(config['comment_text']['x'], config['comment_text']['y'])
    time.sleep(1)
    # 输入上面msg内容 ，注意要使用ADB keyboard  否则不能自动输入，参考： https://www.jianshu.com/p/2267adf15595
    cmd = 'shell am broadcast -a ADB_INPUT_TEXT --es msg {text}'.format(text=msg)
    adb.run(cmd)
    time.sleep(1)
    # 点击发送按钮
    tap(config['comment_send']['x'], config['comment_send']['y'])
    time.sleep(0.5)

    # 触发返回按钮, keyevent 4 对应安卓系统的返回键，参考KEY 对应按钮操作：  https://www.cnblogs.com/chengchengla1990/p/4515108.html
    cmd = 'shell input keyevent 4'
    adb.run(cmd)

def main():
    global forMat
    print('程序版本号：{}'.format(VERSION))
    debug.dump_device_info()
    screenshot.check_screenshot()

    while True:
        next_page()

        time.sleep(2)
        screenshot.pull_screenshot()

        resize_image('autojump.png', 'optimized.png', 1024 * 1024)

        with open('optimized.png', 'rb') as bin_data:
            image_data = bin_data.read()

        ai_obj = apiutil.AiPlat(config['api']['SecretId'], config['api']['SecretKey'])
        rsp = ai_obj.face_detectface(image_data)

        major_total = 0
        minor_total = 0

        if rsp['ret'] == 0:
            beauty = 0

            for s in rsp["FaceInfos"]:
                face = s["FaceAttributesInfo"]

                print(face)

                msg_log = '[INFO] gender: {gender} age: {age} expression: {expression} beauty: {beauty}'.format(
                    gender=face['Gender'],
                    age=face['Age'],
                    expression=face['Expression'],
                    beauty=face['Beauty'],
                )
                print(msg_log)
                face_area = (s['X'], s['Y'], s['X'] + s['Width'], s['Y'] + s['Height'])
                img = Image.open("optimized.png")
                cropped_img = img.crop(face_area).convert('RGB')
                cropped_img.save(FACE_PATH + uuid1().__str__() + '.png')
                # 性别判断
                if face['Beauty'] > beauty and face['Gender'] < 50:
                    beauty = face['Beauty']

                if face['Age'] > GIRL_MIN_AGE:
                    major_total += 1
                else:
                    minor_total += 1

            # 是个美人儿~关注点赞走一波
            if beauty > BEAUTY_THRESHOLD and major_total > minor_total:
                print('发现漂亮妹子！！！')
                thumbs_up(config['star'])
                follow_user(config['follow'])
                reply(config['comment'])

        else:
            print(rsp)
            continue


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        adb.run('kill-server')
        print('谢谢使用')
        exit(0)
