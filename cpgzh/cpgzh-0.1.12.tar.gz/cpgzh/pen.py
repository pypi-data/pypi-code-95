import os
import sys

import pygame
import pygame.draw
from pgzero import loaders, ptext
from pgzero.rect import Rect


def round_xy(pos):
    '四舍五入坐标'
    if isinstance(pos, tuple):
        x, y = pos
        return(round(x), round(y))
    else:
        return(round(pos))


class Font:
    '字体样式类'

    def __init__(self) -> None:
        '初始化字体样式'
        self.styles = {}
        path = os.path.join(loaders.root, 'fonts')
        if os.path.isdir(path):
            self.fonts = os.listdir(path)
            self.fontname = self.fonts[-1]  # 字体名字
        else:
            self.fonts = []
            self.fontname = None
        self.bold = None  # 加粗
        self.italic = None  # 斜体
        self.underline = None  # 下划线
        self.color = 'black'  # 字体颜色
        self.gcolor = None  # 渐变色
        self.ocolor = None  # 边框颜色
        self.scolor = None  # 阴影颜色
        self.align = 'left'  # 左对齐
        self.alpha = 1.0  # 不透明度
        self.angle = 0  # 旋转角度
        self.owidth = None  # 边框宽度
        self.shadow = (0.0, 0.0)  # 阴影，x方向和y方向
        self.fontsize = 30  # 字体大小
        self.sysfonts = pygame.font.get_fonts()  # 所有系统字体
        self.sysfontname = self.sysfonts[-1]  # 设置系统字体

    def __setattr__(self, name, value) -> None:
        '重写设置属性的方法'
        self.__dict__[name] = value
        if not name in ['sysfonts', 'styles', 'fonts']:
            self.styles[name] = value


class Pen:
    def __init__(self) -> None:
        self.mod = sys.modules['__main__']

    def dot(self, pos, radius, color):
        '绘制一个点，参数依次为：中心坐标，直径，颜色'
        pos = round_xy(pos)
        self.circle(pos, radius, color, 0)

    def line(self, start, end, color, border=1):
        '绘制一条线，参数依次为：起点、终点、颜色、宽度'
        start = round_xy(start)
        end = round_xy(end)
        surf = self.mod.screen.surface
        pygame.draw.line(surf, color, start, end, border)

    def circle(self, pos, radius, color, border=1):
        '''
        绘制圆圈或者圆环，参数依次为：圆心坐标、直径、颜色、圆环宽度\n
        border参数默认为1，会绘制宽度为1的圆圈\n
        border参数设置成0，绘制实心圆\n
        '''
        pos = round_xy(pos)
        surf = self.mod.screen.surface
        pygame.draw.circle(surf, color, pos, radius, border)

    def ellipse(self, pos, width, height, color, border=1):
        '''
        绘制椭圆，参数依次为：中心坐标，宽度、高度、颜色、边框宽度\n
        border参数默认为1，会绘制宽度为1的椭圆\n
        border参数设置成0，绘制实心椭圆\n
        '''
        pos = round_xy(pos)
        surf = self.mod.screen.surface
        x = pos[0]-width/2
        y = pos[1]-height/2
        rect = Rect(x, y, width, height)
        pygame.draw.ellipse(surf, color, rect, border)

    def rect(self, pos, width, height, color, border=1, radius=0):
        '''
        绘制长方形或者正方形，参数以此为：中心坐标、宽度、高度、颜色、边框宽度、圆角半径\n
        边框宽度、圆角半径默认为1和0,会绘制一个边框为1没有圆角的方形\n
        '''
        pos = round_xy(pos)
        surf = self.mod.screen.surface
        x = pos[0]-width/2
        y = pos[1]-height/2
        rect = Rect(x, y, width, height)
        pygame.draw.rect(surf, color, rect, border, radius)

    def text(self, text, font=None, *args, **kwargs):
        '''
        写字(仅文本模式)\n  
        text参数是你要写的文字\n
        font是字体，实例化的Font类，如果不传递就会使用默认样式\n
        位置参数也必须传递，传递的时候参考Actor类的传递方式\n
        其他相关参数也可以手动传递
        '''
        # FIXME: expose ptext parameters, for autocompletion and autodoc
        if not font:
            font = Font()
        surf = self.mod.screen.surface
        kwargs.update(font.styles)
        kwargs['text'] = text
        ptext.draw(surf=surf, *args, **kwargs)

    def textbox(self, text, font=None, *args, **kwargs):
        '''
        写字(文本框模式)\n
        text参数是你要写的文字\n
        font是字体，实例化的Font类，如果不传递就会使用默认样式\n
        位置参数也必须传递，传递的时候参考Actor类的传递方式\n
        其他相关参数也可以手动传递
        '''
        # FIXME: expose ptext parameters, for autocompletion and autodoc
        if not font:
            font = Font()
        surf = self.mod.screen.surface
        kwargs.update(font.styles)
        kwargs['text'] = text
        ptext.drawbox(surf=surf, *args, **kwargs)
