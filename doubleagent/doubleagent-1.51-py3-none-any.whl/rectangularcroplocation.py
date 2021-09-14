
from PIL import Image, ImageOps, ImageFile, ImageDraw, ImageFont
import numpy as np


def rectangularcroplocation(png):
    xx, yy = png.size
    imgArray = np.array(png)
    nomal = imgArray.tolist()
    count = 0
    for y, li1 in enumerate(nomal):

        if count == 1:
            break
        for x, li2 in enumerate(li1):
            if count == 1:
                break

            if not li2[3] == 0:
                y1 = y

                count = 1

    lotate90 = png.transpose(Image.ROTATE_270)
    lotate90 = np.array(lotate90)
    lotate90 = lotate90.tolist()
    count = 0
    for y, li1 in enumerate(lotate90):

        if count == 1:
            break
        for x, li2 in enumerate(li1):
            if count == 1:
                break

            if not li2[3] == 0:
                x1 = y

                count = 1

    lotate180 = png.transpose(Image.ROTATE_180)
    lotate180 = np.array(lotate180)
    lotate180 = lotate180.tolist()
    count = 0
    for y, li1 in enumerate(lotate180):

        if count == 1:
            break
        for x, li2 in enumerate(li1):
            if count == 1:
                break

            if not li2[3] == 0:
                y2 = y

                count = 1

    lotate90 = png.transpose(Image.ROTATE_90)
    lotate90 = np.array(lotate90)
    lotate90 = lotate90.tolist()
    count = 0
    for y, li1 in enumerate(lotate90):

        if count == 1:
            break
        for x, li2 in enumerate(li1):
            if count == 1:
                break

            if not li2[3] == 0:
                x2 = y

                count = 1

    return x1, y1, xx-x2, yy-y2
