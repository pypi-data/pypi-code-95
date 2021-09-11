import sys

import guizero
import pygame
import pygame.draw
from guizero import App
from .data import Data


def round_xy(pos):
    '四舍五入坐标'
    if isinstance(pos, tuple):
        x, y = pos
        return(round(x), round(y))
    else:
        return(round(pos))


class Master:
    def __init__(self, data_path='data.dat') -> None:
        '管家类，负责一些管理类的功能'
        self._fullscreen = False
        self.data = Data(data_path)
        self.load_data()
        self.data.temp = ''
        self.app = App(visible=False)
        self.mod = sys.modules['__main__']

    @property
    def data_path(self):
        '获取data_path'
        return self.data.data_path

    @data_path.setter
    def data_path(self, path):
        '设置data_path'
        print(f'数据地址{path}')
        self.data.data_path = path

    def load_data(self):
        '加载数据'
        self.data.load_data()

    def save_data(self):
        '保存数据'
        self.data.save_data()

    def del_data(self):
        '删除数据'
        self.data.del_data()

    def set_fullscreen(self) -> None:
        '设置全屏'
        self.mod.screen.surface = pygame.display.set_mode(
            (self.mod.WIDTH, self.mod.HEIGHT), pygame.FULLSCREEN)
        self._fullscreen = True

    def set_windowed(self) -> None:
        '设置窗口化'
        self.mod.screen.surface = pygame.display.set_mode(
            (self.mod.WIDTH, self.mod.HEIGHT))
        self._fullscreen = False

    def toggle_fullscreen(self) -> None:
        '切换全屏和窗口化'
        if self._fullscreen:
            self.set_windowed()
        else:
            self.set_fullscreen()

    def hide_mouse(self) -> None:
        '隐藏鼠标'
        pygame.mouse.set_visible(False)

    def show_mouse(self) -> None:
        '显示鼠标'
        pygame.mouse.set_visible(True)

    def input(self, msg='请输入数据：') -> str:
        '简单输入框'
        text = guizero.askstring('输入', msg)
        self.data.temp = text
        return text

    def select_file(self, msg='请选择文件', filetypes=[["All files", "*.*"]]) -> str:
        '''
        选择文件，filetypes是文件类型，比如：   

        filetypes=[["All files", "*.*"]]    

        不想限定的话，就不传递这个参数。  
        '''
        file = guizero.select_file(
            '请选择一个文件', filetypes=filetypes, master=self.app)
        self.data.temp = file
        return file

    def select_file_save(self, msg='请选择文件', filetypes=[["All files", "*.*"]]) -> str:
        '''
        保存文件的选择提示框，filetypes是文件类型，比如：   

        filetypes=[["All files", "*.*"]]    

        不想限定的话，就不传递这个参数。  
        '''
        path = guizero.select_file(
            '请选择一个文件', filetypes=filetypes, save=True, master=self.app)
        self.data.temp = path
        return path

    def select_dir(self, msg='请选择文件夹') -> str:
        '选择一个文件夹'
        dir = guizero.select_folder('请选择一个文件夹', master=self.app)
        self.data.temp = dir
        return dir

    def yes_no(self, msg='是否？'):
        '是否做某件事的选择框'
        yes_or_no = guizero.yesno('请选择', msg, master=self.app)
        self.data.temp = yes_or_no
        return yes_or_no

    def msg(self, msg='这是提示信息'):
        '提示信息'
        guizero.info('提示', msg, master=self.app)

    def warning(self, msg='这是警告信息'):
        '警告信息'
        guizero.warn('警告', msg, master=self.app)

    def error(self, msg='这是错误信息'):
        '错误信息'
        guizero.error('错误', msg, master=self.app)
