import sys
import ctypes

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

# 字体颜色定义 ,关键在于颜色编码，由2位十六进制组成，分别取0~f，前一位指的是背景色，后一位指的是字体色
# 由于该函数的限制，应该是只有这16种，可以前景色与背景色组合。也可以几种颜色通过或运算组合，组合后还是在这16种颜色中

# Windows CMD命令行 字体颜色定义 text colors
FOREGROUND_BLACK = 0x00
FOREGROUND_DARKBLUE = 0x01
FOREGROUND_DARKGREEN = 0x02
FOREGROUND_DARKSKYBLUE = 0x03
FOREGROUND_DARKRED = 0x04
FOREGROUND_DARKPINK = 0x05
FOREGROUND_DARKYELLOW = 0x06
FOREGROUND_DARKWHITE = 0x07
FOREGROUND_DARKGRAY = 0x08
FOREGROUND_BLUE = 0x09
FOREGROUND_GREEN = 0x0A
FOREGROUND_SKYBLUE = 0x0B
FOREGROUND_RED = 0x0C
FOREGROUND_PINK = 0x0D
FOREGROUND_YELLOW = 0x0E
FOREGROUND_WHITE = 0x0F

# Windows CMD命令行 背景颜色定义 background colors
BACKGROUND_BLACK = 0x10
BACKGROUND_DARKGREEN = 0x20
BACKGROUND_DARKSKYBLUE = 0x30
BACKGROUND_DARKRED = 0x40
BACKGROUND_DARKPINK = 0x50
BACKGROUND_DARKYELLOW = 0x60
BACKGROUND_DARKWHITE = 0x70
BACKGROUND_DARKGRAY = 0x80
BACKGROUND_BLUE = 0x90
BACKGROUND_GREEN = 0xA0
BACKGROUND_SKYBLUE = 0xB0
BACKGROUND_RED = 0xC0
BACKGROUND_PINK = 0xD0
BACKGROUND_YELLOW = 0xE0
BACKGROUND_WHITE = 0xF0

# get handle
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool


# reset white
def resetColor():
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)


def _exec(color, value):
    set_cmd_text_color(color)
    sys.stdout.write(str(value))
    resetColor()

# ------------------------------------------------------------------------------


# 暗蓝
def darkBlue(value):
    _exec(FOREGROUND_DARKBLUE, value)


# 暗绿
def darkGreen(value):
    _exec(FOREGROUND_DARKGREEN, value)


# 暗天蓝
def darkSkyBlue(value):
    _exec(FOREGROUND_DARKSKYBLUE, value)


# 暗红
def darkRed(value):
    _exec(FOREGROUND_DARKRED, value)


# 暗粉红
def darkPink(value):
    _exec(FOREGROUND_DARKPINK, value)


# 暗黄
def darkYellow(value):
    _exec(FOREGROUND_DARKYELLOW, value)


# 暗白
def darkWhite(value):
    _exec(FOREGROUND_DARKWHITE, value)


# 暗灰
def darkGray(value):
    _exec(FOREGROUND_DARKGRAY, value)


# 蓝
def blue(value):
    _exec(FOREGROUND_BLUE, value)


# 绿
def green(value):
    _exec(FOREGROUND_GREEN, value)


# 天蓝
def skyBlue(value):
    _exec(FOREGROUND_SKYBLUE, value)


# 红
def red(value):
    _exec(FOREGROUND_RED, value)


# 粉红
def pink(value):
    _exec(FOREGROUND_PINK, value)


# 黄
def yellow(value):
    _exec(FOREGROUND_YELLOW, value)


# 白
def white(value):
    _exec(FOREGROUND_WHITE, value)


# ------------------------------------------------------------------------------


# 白底黑字
def whiteBlack(value):
    _exec(FOREGROUND_BLACK | BACKGROUND_WHITE, value)


# 白底黑字
def whiteBlack_2(value):
    _exec(0xF0, value)


# 黄底蓝字
def yellowRed(value):
    _exec(BACKGROUND_YELLOW | FOREGROUND_RED, value)
