# coding: utf-8

from PIL import Image, ImageDraw, ImageFont

CHARS = list("@%#*+=-:. ")


def makeImage(
    imgPath: str,
    savePath: str,
    scale: float = 1,
    fontPath: str = "",
    fontSize: int = 20,
    horzSep=2,
    vertSep=2,
    keepRatio=True,
    keepSize=False,
):
    if not (isinstance(horzSep, int) and isinstance(vertSep, int)):
        raise TypeError("The char interval [horzSep], [vertSep] must be int.")
    if not (0 <= horzSep <= 10 and 0 <= vertSep <= 10):
        raise ValueError("The character interval must be between 0 and 10.")
    if not isinstance(scale, (int, float)) or (not 0 < scale <= 1):
        raise ValueError("The zoom ratio [scale] must be a number > 0 and <= 1.")
    if fontPath:
        imgFont = ImageFont.truetype(fontPath, fontSize)
    else:
        imgFont = ImageFont.load_default()
    ftWidth, ftHeight = imgFont.getsize(CHARS[0])
    # 往图片写入字符时横坐标的移动增量
    hIncrement = ftWidth + horzSep
    # 往图片写入字符时纵坐标的移动增量
    vIncrement = ftHeight + vertSep
    image = Image.open(imgPath).convert("L")
    imageWidth, imageHeight = image.size
    if keepRatio:
        # 按字符的宽高(加分隔距离)比例来计算原图需要缩放的比例
        imageHeight = round(hIncrement / vIncrement * imageHeight)
    if scale != 1:
        imageWidth = round(imageWidth * scale)
        imageHeight = round(imageHeight * scale)
    if keepRatio or scale != 1:
        image = image.resize((imageWidth, imageHeight), Image.NEAREST)
    lenChars, charList = len(CHARS), list()
    for y in range(imageHeight):
        for x in range(imageWidth):
            grayNum = image.getpixel((x, y))
            charIndex = round((grayNum / 255) * (lenChars - 1))
            charList.append(CHARS[charIndex])
    newWidth = (ftWidth + horzSep) * imageWidth + horzSep
    newHeight = (ftHeight + vertSep) * imageHeight + vertSep
    newImage = Image.new("L", (newWidth, newHeight), 255)
    drawPanel = ImageDraw.Draw(newImage)
    x, y = horzSep, vertSep
    for index, char in enumerate(charList):
        if index != 0 and not (index % imageWidth):
            x = horzSep
            y += vIncrement
        drawPanel.text((x, y), char, 0, imgFont)
        x += hIncrement
    if keepSize:
        newImage.resize((imageWidth, imageHeight), Image.ANTIALIAS)
    newImage.save(savePath)
