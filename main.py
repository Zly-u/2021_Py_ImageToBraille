# -*- coding: utf8 -*-
import math

from PIL import Image
import os
import glob
import io
import datetime


cur_script_path = os.path.dirname(os.path.abspath(__file__))
images = glob.glob(cur_script_path + "\\imageSequence\\*.png")
#print(images)

startByte = 0x2800

pallete_mate = [
    [
        (True, True),
        (True, True),
        (True, True),
        (True, True)
    ],
    [
        (True, False),
        (True, True),
        (True, True),
        (True, True)
    ],
    [
        (True, True),
        (False, True),
        (True, False),
        (True, True)
    ],
    [
        (True, True),
        (False, True),
        (True, False),
        (False, True)
    ],
    [
        (True, False),
        (False, True),
        (True, False),
        (False, True)
    ],
    [
        (False, True),
        (False, False),
        (True, False),
        (False, True)
    ],
[
        (False, True),
        (False, False),
        (True, False),
        (False, False)
    ],
[
        (False, False),
        (False, True),
        (True, False),
        (False, False)
    ],
    [
        (False, False),
        (True, False),
        (False, False),
        (False, False)
    ],
    # [
    #     (False, False),
    #     (False, False),
    #     (False, False),
    #     (False, False)
    # ],
    # [
    #     (False, False),
    #     (False, False),
    #     (False, False),
    #     (False, False)
    # ],
]

word = [
    [
        (True, False),
        (True, False),
        (False, False),
        (False, False)
    ],
    [
        (True, False),
        (False, False),
        (False, False),
        (False, False)
    ],
    [
        (True, True),
        (False, True),
        (False, False),
        (False, False)
    ],
    [
        (False, False),
        (False, False),
        (False, False),
        (False, False)
    ],
    [
        (True, True),
        (True, False),
        (True, False),
        (False, False)
    ],
    [
        (True, False),
        (False, True),
        (True, False),
        (False, False)
    ],
    [
        (True, True),
        (False, False),
        (False, False),
        (False, False)
    ],
    [
        (True, False),
        (True, False),
        (True, False),
        (False, False)
    ],
    [
        (True, False),
        (False, False),
        (True, False),
        (False, False)
    ],
]

#TODO: Threasholds?
def convertColorToBraille(x):
    next_char = 0b00000000
    for i, row in enumerate(x):
        threashold = 0.0
        row0_c = row[0] / 255.0
        row1_c = row[1] / 255.0
        row0 = row0_c >= 1.0 - threashold
        row1 = row1_c >= 1.0 - threashold

        next_char |= (0b00000001 << i)         * (1 if row0 else pallete_mate[8][i][0])
        next_char |= (0b00000001 << (4 + i))   * (1 if row1 else pallete_mate[8][i][1])

    flag = 0b0
    flag += (next_char & 0b00001000) << 3
    flag += (next_char & 0b01110000) >> 1
    flag += (next_char & 0b10000111)

    return chr(startByte + flag)

def convertColorToBrailleWDith(x, invert=False):
    next_char = 0b00000000
    for i, row in enumerate(x):
        colors = len(pallete_mate) - 1

        row0_c = row[0] / 255.0
        row1_c = row[1] / 255.0

        dith_mate0 = pallete_mate[int(colors - row0_c * colors if not invert else row0_c * colors)][i][0]
        dith_mate1 = pallete_mate[int(colors - row1_c * colors if not invert else row1_c * colors)][i][1]

        next_char |= (0b00000001 << i) * dith_mate0
        next_char |= (0b00000001 << (4 + i)) * dith_mate1

    flag = 0b0
    flag += (next_char & 0b00001000) << 3
    flag += (next_char & 0b01110000) >> 1
    flag += (next_char & 0b10000111)

    return chr(startByte + flag)

def convertArrayToBraille(x):
    next_char = 0b00000000
    for i, row in enumerate(x):
        next_char |= (row[0] * 0b00000001) << i
        next_char |= (row[1] * 0b00000001) << 4 + i

    flag = 0b0
    flag += (next_char & 0b00001000) << 3
    flag += (next_char & 0b01110000) >> 1
    flag += (next_char & 0b10000111)

    return chr(startByte + flag)




for dith in word:
    print(convertArrayToBraille(dith), end="")


def convertImageToBraille(pixel_data, invert=False):
    screen = ""
    for y in pixel_data:
        line = ""
        for x in y:
            line += convertColorToBrailleWDith(x, invert=invert)
        screen += line+"\n"
    return screen

def convertImageToBrailleFS(pixel_data, invert=False):
    screen = ""
    for y in pixel_data:
        line = ""
        for x in y:
            line += convertColorToBraille(x)
        screen += line+"\n"
    return screen

def getImageInfo(image):
    image_data = Image.open(image)
    size = image_data.size

    pixel_data = []
    scale = 1
    comp_scale = 1/scale
    xdiv = 2+1
    ydiv = 4+1
    for y in range(int((size[1]/ydiv)*scale)):
        row = []
        for x in range(int((size[0]/xdiv)*scale)):
            cell = []
            for yi in range(4):
                cell.append((
                    (image_data.getpixel((
                        int((x*xdiv)*comp_scale),
                        int((y*ydiv+yi)*comp_scale)
                    )))[0],
                    (image_data.getpixel((
                        int((x*xdiv+1)*comp_scale),
                        int((y*ydiv+yi)*comp_scale)
                    ))[0]
                )))
            row.append(cell)
        pixel_data.append(row)
    return pixel_data

FS_colors = 8
FS_pallete = [int((255/FS_colors)*i) for i in range(1, FS_colors+1)]
print(FS_pallete)

#idk if this works lol
def bw_threshold(val):
    threshold = 0.2
    if val/255 <= threshold:
        return math.floor(val)
    if val/255 >= 1-threshold:
        return math.ceil(val)
    return math.trunc(val)


#TODO: Threasholds?
def FloydSteinbergDithering(image_data, scale):
    pixel_data = image_data.load()
    size_x, size_y = image_data.size

    comp_scale = 1
    # xdiv = 2 + 1
    # ydiv = 4 + 1
    for y in range(1, size_y):
        for x in range(1, size_x):
            oldpixel = pixel_data[x, y][0]
            # newpixel = 255 * math.floor(oldpixel/128)
            newpixel = math.trunc(oldpixel/255 +0.5)*255
            pixel_data[x, y] = (newpixel, 0, 0)
            quant_error = oldpixel - newpixel

            _x  = int(x*comp_scale)
            _xp = int((x+1)*comp_scale)
            _xn = int((x-1)*comp_scale)
            _y  = int(y*comp_scale)
            _yp = int((y+1)*comp_scale)
            # print(_x, _xp, _xn, _y, _yp)
                                                                                                            #TODO: here i gueessss
            if _x < size_x - 1:                      pixel_data[_xp, _y]     = (bw_threshold(pixel_data[_xp, _y][0]   + round(quant_error * 7 / 16)), 0, 0)
            if _x > 1 and _y < size_y - 1:           pixel_data[_xn, _yp]    = (bw_threshold(pixel_data[_xn, _yp][0]  + round(quant_error * 3 / 16)), 0, 0)
            if _y < size_y - 1:                      pixel_data[_x,  _yp]    = (bw_threshold(pixel_data[_x,  _yp][0]  + round(quant_error * 5 / 16)), 0, 0)
            if _x < size_x - 1 and _y < size_y - 1:  pixel_data[_xp, _yp]    = (bw_threshold(pixel_data[_xp, _yp][0]  + round(quant_error * 1 / 16)), 0, 0)

def getImageInfoFS(image):
    scale = 0.1

    image_data = Image.open(image)
    FloydSteinbergDithering(image_data, scale)
    size = image_data.size

    pixel_data = []
    comp_scale = 1/scale
    xdiv = 2+1
    ydiv = 4+1
    for y in range(int((size[1]/ydiv)*scale)):
        row = []
        for x in range(int((size[0]/xdiv)*scale)):
            cell = []
            for yi in range(4):
                cell.append((
                    (image_data.getpixel((
                        int((x*xdiv)*comp_scale),
                        int((y*ydiv+yi)*comp_scale)
                    )))[0],
                    (image_data.getpixel((
                        int((x*xdiv+1)*comp_scale),
                        int((y*ydiv+yi)*comp_scale)
                    ))[0]
                )))
            row.append(cell)
        pixel_data.append(row)
    return pixel_data

'''
3
00:00:06,770 --> 00:00:10,880
ЭЛИС: Сегодня мы научим вас готовить
наше знаменитое шоколадное печенье.
'''

def createYTSubtitlesLol(image_list):
    fps = 29.970
    spf = 1.0/fps

    file        = io.open(cur_script_path + "\\subs.txt", mode="w", encoding="utf8")
    prev_time   = 0.001
    amount_of_imgs = len(image_list)
    for index, image in enumerate(image_list, 1):
        start_time = datetime.datetime.now()

        data    = getImageInfoFS(image)
        out     = convertImageToBrailleFS(data, invert=False)

        cur_time = spf*index
        formatted_prev_time = (str(datetime.timedelta(seconds=prev_time)).replace('.', ','))[:-3]
        formatted_dur_time  = (str(datetime.timedelta(seconds=cur_time)).replace('.', ','))[:-3]

        prev_time = cur_time

        caption = f"{index}\n{formatted_prev_time} --> {formatted_dur_time}\n{out}\n"
        file.writelines(caption)

        bars = 50
        bar_str = "⣿"
        bar_str_empty = "⠁"
        progress = ((bars/amount_of_imgs)*index)/bars
        time_passed = datetime.datetime.now()-start_time
        print("["+ (bar_str_empty*bars).replace(bar_str_empty, bar_str, int(progress*bars)) +"]: "+ str(progress*100)[:4]+"% | " +
              str(index)+ "/" +str(amount_of_imgs) + " | " + str(time_passed.seconds+(time_passed.microseconds/1000000)) + " sec")

    file.flush()
    file.close()


def main():
    # data = getImageInfo(images[1326])
    # out = convertImageToBraille(data, invert=False)
    # data = getImageInfoFS(images[1326])
    # out = convertImageToBrailleFS(data, invert=False)
    #
    # file = io.open(cur_script_path+"\\output.txt", mode="w", encoding="utf8")
    # file.writelines(out)
    # file.flush()
    # file.close()

    createYTSubtitlesLol(images)

    # pass

if __name__ == "__main__":
    main()