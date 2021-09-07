# -*- coding: utf-8 -*-

'''
项目介绍:
开发者　: Yogurt_cry
'''

from clr import AddReference

win64ControlQianniuPath = r'pyAppControl/Win64ControlQianniu/Win64ControlQianniu' # 部署环境
AddReference(win64ControlQianniuPath)

import Win64ControlQianniu

from pyAppControl.Qianniu import Qianniu

__title__ = 'pyAppControl'
__description__ = '基于 C# 开发的客户端控制程序。用于给一些存在大量重复性的软件操作场景提供技术支持。后续会逐渐提供相应的 App 控制解决方案。仅支持 x64 位 Windows 系统'
__url__ = 'https://gitee.com/Yogurt_cry/pyAppControl'
__version__ = '1.0.0'
__build__ = ''
__author__ = 'Yogurt_cry'
__author_email__ = 'ben.2001@foxmail.com'
__license__ = 'MIT License'
__copyright__ = 'CCSDESIGN'
