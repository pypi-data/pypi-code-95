'''
教学用turtle辅助库
'''
from random import randint
import turtle
import math
import string
import time

turtle.ht()
turtle.colormode(255)
CURRENTPEN = None  # 最近一次使用的画笔
SCR_W = None  # 窗口宽度
SCR_H = None  # 窗口高度
POSITION = None  # 字典，用常量表示窗口位置，例如lt是左上角


class PenException(RuntimeError):
    '''
    自定义画笔异常
    '''
    pass


def check_pen(func):
    '''
    装饰器
    库中的许多绘图函数都需要传入画笔作为第一个参数
    装饰器会检查第一个参数类型是否为Turtle对象
    如果不是，则尝试使用最近一次使用的画笔进行绘制
    如果最近一次画笔为None，则抛出PenException
    要求使用者传入一支”画笔“，即Turtle对象
    '''
    def check(t, *args, **kwargs):

        if isinstance(t, turtle.Turtle):  # 如果第一个参数是Turtle类型
            global CURRENTPEN
            CURRENTPEN = t  # 这只画笔将作为最近一次使用的画笔
            return func(t, *args, **kwargs)
        elif CURRENTPEN:
            # 第一个参数t不是笔，即用户调用func函数时忘记传入笔了
            # 如果此时CURRENTPEN不为None，那么就使用最近一次使用过的画笔来画。
            return func(CURRENTPEN, t, *args, **kwargs)
        else:
            # 否则抛出异常
            raise PenException('need a pen')

    return check


@check_pen
def rect(t, w, h=None, fill=True, flag=True):
    '''
    绘制矩形
    
    参数说明：
    t 画笔，即Turtle对象 
    w 矩形宽度 可以传入数字，也可以传入元组，元组的第一个数字为宽度，第二个数字为高度
    h 矩形高度，可以省略。如果w是元组，则第二个元素是高度。如果w是数字则h与w相同
    fill 是否填充，默认是填充
    flag 旋转方式，默认是顺时针旋转
    '''
    if h is None:
        if isinstance(w, tuple):
            w = w[0]
            h = w[1]
        else:
            h = w

    if fill:
        t.begin_fill()
    for x in range(2):
        t.fd(w)
        if flag:
            t.right(90)
        else:
            t.left(90)
        t.fd(h)
        if flag:
            t.right(90)
        else:
            t.left(90)
    if fill:
        t.end_fill()


@check_pen
def square(t, size, fill=True, flag=True):
    '''
    绘制正方形

    参数说明：
    t 画笔，即Turtle对象
    size 正方形边长
    fill 是否填充，默认填充
    flag 选择方向，默认顺时针
    '''
    if fill:
        t.begin_fill()

    for x in range(4):

        t.fd(size)
        if flag:
            t.right(90)
        else:
            t.left(90)
    if fill:
        t.end_fill()


@check_pen
def sector(t, size, ag=90, fill=True):
    '''
    绘制扇形

    参数说明：
    t 画笔，Turtle对象
    size 扇形半径大小
    ag  扇形圆心角大小，默认90度
    fill 是否填充，默认填充
    '''
    ag = ag % 360
    if fill:
        t.begin_fill()
    t.circle(size, ag)
    t.left(90)
    t.fd(size)
    t.left(180 - ag)
    t.fd(size)
    if fill:
        t.end_fill()


@check_pen
def polygon(t, size, nums=6, fill=True, flag=True):
    '''
    绘制多边形

    参数说明：
    t 画笔，Turtle对象
    size 多边形边长
    nums 多边形边数，默认6
    fill 是否填充，默认填充
    flag 旋转方向，默认顺时针
    '''
    if fill:
        t.begin_fill()
    for i in range(nums):
        t.fd(size)
        if flag:
            t.right(360 / nums)
        else:
            t.left(360 / nums)
    if fill:
        t.end_fill()


@check_pen
def triangle(t, size, flag=True):
    '''
    绘制三角形

    参数说明：
    t 画笔，Turtle对象
    size 三角形边长
    flag 旋转方向，默认顺时针
    '''
    for x in range(3):
        t.fd(size)
        if flag:
            t.right(120)
        else:
            t.left(120)


@check_pen
def star(t, size, fill=True, flag=True):
    '''
    绘制五角星

    参数说明：
    t 画笔，Turtle对象
    size 五角星边长
    fill 是否填充，默认填充
    flag 旋转方向，默认顺时针
    '''

    if fill:
        t.begin_fill()
    for x in range(5):
        t.fd(size)
        if flag:
            t.right(144)
        else:
            t.left(144)
    if fill:
        t.end_fill()


def randco(minx=None, miny=None):
    '''
    生成绘图窗范围内的随机坐标

    参数说明：
    x   用来指定横坐标的下限，默认横坐标下限是绘图窗左边缘
    y   用来指定纵坐标的下限，默认纵坐标下限是绘图窗下边缘
    '''
    scr = turtle.getscreen()
    w = scr.window_width()
    h = scr.window_height()
    if minx is None:
        minx = -w // 2
    if miny is None:
        miny = -h // 2
    xpos = randint(minx, w // 2)
    ypos = randint(miny, h // 2)
    return (xpos, ypos)


@check_pen
def flower(t, size, nums=5, ic='yellow'):
    '''
    绘制花朵

    参数说明：
    t 画笔，Turtle对象
    size 花朵的半径大小
    nums 花朵的花瓣数 默认是5瓣
    ic  花芯的颜色 默认是黄色
    '''
    c = t.color()
    t.begin_fill()
    for i in range(nums):
        t.circle(size)
        t.left(360 / nums)
    t.end_fill()
    t.color(ic)
    t.dot(size)
    t.color(c[0])


@check_pen
def polywrite(t, poem, font=('楷体', 10)):
    '''
    多边形写诗

    参数说明：
    t 画笔，Turtle对象
    poem 诗文 诗句间应该用空格进行分割，每一个诗句是多边形的一条边
    font 使用的字体 默认为楷体，10号字
    '''
    lines = poem.split()
    angle = 360 / len(lines)
    if font[1]:
        size = int(font[1]) * 1.6
    else:
        raise RuntimeError('please set font')
    t.up()
    for line in lines:
        for word in line:
            t.write(word, font=font)
            t.fd(size)
        t.right(angle)
    t.pd()


@check_pen
def circlewrite(t, poem, font=('楷体', 10)):
    '''
    圆形写诗

    参数说明：
    t 画笔，Turtle对象
    poem 诗文
    font 使用的字体 默认为楷体，10号字
    '''

    l = len(poem)
    t.up()
    if font[1]:
        size = int(font[1]) * 10
    else:
        raise RuntimeError('please set font')
    for x in poem:
        t.write(x, font=font)
        t.circle(-size, 360 / l)
    t.down()


@check_pen
def bg(t):
    '''
    绘制绘图窗背景色

    参数说明：
    t 画笔，Turtle对象
    '''
    scr = turtle.getscreen()
    w = scr.window_width()
    h = scr.window_height()
    x = t.xcor()
    y = t.ycor()
    t.up()
    t.goto(-w / 2, h / 2)
    t.begin_fill()
    for i in range(2):
        t.fd(w)
        t.right(90)
        t.fd(h)
        t.right(90)
    t.end_fill()
    t.goto(x, y)


@check_pen
def heart(t, size=30, angle=0, fill=True):
    '''
    绘制心形

    参数说明：
    t 画笔，Turtle对象
    size 心形大小（心形圆弧的半径大小），默认的大小为30
    angle 起笔的旋转角度，用来绘制有一定角度的爱心，默认值0度
    fill 是否填充，默认填充

    '''
    if angle:
        myheading = t.heading()
        t.left(angle)
    if fill:
        t.begin_fill()
    t.left(45)
    t.fd(size * 2)
    t.circle(size, 180)
    t.right(90)
    t.circle(size, 180)
    t.fd(size * 2)
    t.left(45)
    if fill:
        t.end_fill()

    if angle:
        t.seth(myheading)


@check_pen
def move(t, m, *args):
    '''
    移动画笔到指定位置

    参数说明：
    t 画笔，Turtle对象
    m 目的坐标，可以传入元组也可以传入两个数字，还可以传入位置的文字说明

    '''
    t.up()
    if isinstance(m, tuple):
        t.goto(m[0], m[1])
    elif isinstance(m, str):
        if POSITION is None:
            raise RuntimeError('请先获得画笔')
        else:
            t.goto(POSITION[m])
    else:
        t.goto(m, args[0])
    t.pd()


@check_pen
def stepfd(t, d):
    '''
    画笔沿笔头方向前进

    参数说明：
    t 画笔，Turtle对象
    d 移动的距离

    '''
    t.up()
    t.fd(d)
    t.pd()


@check_pen
def stepbd(t, d):
    '''
    画笔沿笔头方向后退

    参数说明：
    t 画笔，Turtle对象
    d 移动的距离
    
    '''
    t.up()
    t.back(d)
    t.pd()


@check_pen
def _flashrow(t, func, size, sp=0.6):
    turtle.tracer(0)
    while True:
        row(t, func, size)
        turtle.update()
        time.sleep(sp)
        t.clear()


@check_pen
def _row(t, func, size):
    '''
    绘制一行高低略有不同的图案，绘制的图案取决于传入的绘图函数名称
    一行中图案的数量计算，取决于图案的大小和画笔所在位置

    参数说明：
    t 画笔，Turtle对象
    func 绘图函数
    size 绘制的图案大小
    '''
    x = t.xcor()
    y = t.ycor()
    y0 = y + randint(-5, 5)
    move(t, x, y0)

    sw = turtle.getscreen().window_width()

    sh = turtle.getscreen().window_height()
    nums = int(min(8, (sw - x) // (size * 4)))
    if nums != 0:
        step = (sw - x) // (nums * 2)

    if nums == 0:
        func(t, size)
    else:
        for i in range(nums):
            func(t, size)
            move(t, x + step * (i + 1), y + randint(-10, 10))
    t.up()
    t.setpos(x, y)
    t.pd()


@check_pen
def row(t, func, size=10, anim=False):
    if anim:
        _flashrow(t, func, size)
    else:
        _row(t, func, size)


def getpen(color='black', fillcolor=None):
    '''
    获得一支画笔

    调用此方法时，还会为全局变量POSITION SCR_W和SCR_H赋值
    '''
    t = turtle.Turtle()
    global POSITION, SCR_W, SCR_H
    scr = turtle.getscreen()
    SCR_W = scr.window_width()
    SCR_H = scr.window_height()
    POSITION = {
        'c': (0, 0),
        'lt': (-SCR_W / 2, SCR_H / 2),
        'rt': (SCR_W / 2, SCR_H / 2),
        'lb': (-SCR_W / 2, -SCR_H / 2),
        'rb': (SCR_W / 2, -SCR_H / 2),
        'lm': (-SCR_W / 2, 0),
        'rm': (SCR_W / 2, 0),
        'mt': (0, SCR_W / 2),
        'mb': (0, -SCR_H / 2)
    }
    t.ht()
    if fillcolor:
        t.color(color, fillcolor)
    else:
        t.color(color)
    t.speed(0)
    return t


@check_pen
def write(t, c, size=16, style=None, family=None):
    '''
    书写文字。当没有指明具体使用的字体时，如果书写内容为英文或数字，使用Consolas字体
    如果含有其他字符（例如中文），则使用微软雅黑


    参数说明：
    t 画笔，Turtle对象
    c 书写的内容
    size 字号大小，默认字号16
    style 风格 三种风格加粗，倾斜，加粗倾斜，默认没有风格 
    family 字体名称，默认不指定字体名称。

    '''
    flag = 0  #英文
    for ch in c:
        if ch not in string.ascii_letters:
            flag = 1  #有非英文
            break

    if family:
        f = family
    elif flag:
        f = '微软雅黑'
    else:
        f = 'Consolas'

    if style in ['bo', 'bold', 'b']:
        font = (f, size, 'bold')
    elif style in ['it', 'italic', 'i']:
        font = (f, size, 'italic')
    elif style in ['bi', 'boit', 'bold italic']:
        font = (f, size, 'bold italic')
    else:
        font = (f, size)
    t.write(c, font=font)


@check_pen
def tetris_cz(t, x=None, y=None, size=50):
    if x is None:
        x = t.xcor()
    if y is None:
        y = t.ycor()
    move(t, x - 50, y + 50)
    square(t, size)
    move(t, x, y + 50)
    square(t, size)
    move(t, x, y)
    square(t, size)
    move(t, x + 50, y)
    square(t, size)
    move(t, x, y)


@check_pen
def tetris_rz(t, x=None, y=None, size=50):
    if x is None:
        x = t.xcor()
    if y is None:
        y = t.ycor()
    move(t, x + 50, y + 50)
    square(t, size)
    move(t, x, y + 50)
    square(t, size)
    move(t, x, y)
    square(t, size)
    move(t, x - 50, y)
    square(t, size)
    move(t, x, y)


@check_pen
def tetris_or(t, x=None, y=None, size=50):
    if x is None:
        x = t.xcor()
    if y is None:
        y = t.ycor()
    move(t, x + 50, y + 50)
    square(t, size)
    move(t, x + 50, y)
    square(t, size)
    move(t, x, y)
    square(t, size)
    move(t, x - 50, y)
    square(t, size)
    move(t, x, y)


@check_pen
def tetris_br(t, x=None, y=None, size=50):
    if x is None:
        x = t.xcor()
    if y is None:
        y = t.ycor()
    move(t, x - 50, y + 50)
    square(t, size)
    move(t, x - 50, y)
    square(t, size)
    move(t, x, y)
    square(t, size)
    move(t, x + 50, y)
    square(t, size)
    move(t, x, y)


@check_pen
def tetris_h(t, x=None, y=None, size=50):
    if x is None:
        x = t.xcor()
    if y is None:
        y = t.ycor()
    move(t, x, y + 50)
    square(t, size)
    move(t, x, y)
    square(t, size)
    move(t, x, y - 50)
    square(t, size)
    move(t, x, y - 100)
    square(t, size)
    move(t, x, y - 100)


@check_pen
def tetris_t(t, x=None, y=None, size=50):
    if x is None:
        x = t.xcor()
    if y is None:
        y = t.ycor()
    move(t, x - 50, y + 50)
    square(t, size)
    move(t, x, y + 50)
    square(t, size)
    move(t, x + 50, y + 50)
    square(t, size)
    move(t, x, y)
    square(t, size)
    move(t, x, y)


@check_pen
def tetris_s(t, x=None, y=None, size=50):
    if x is None:
        x = t.xcor()
    if y is None:
        y = t.ycor()
    move(t, x - 50, y + 50)
    square(t, size)
    move(t, x, y + 50)
    square(t, size)
    move(t, x - 50, y)
    square(t, size)
    move(t, x, y)
    square(t, size)
    move(t, x, y)