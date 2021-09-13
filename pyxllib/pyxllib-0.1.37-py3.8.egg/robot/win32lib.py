#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author : 陈坤泽
# @Email  : 877362867@qq.com
# @Date   : 2021/09/07 10:21

import win32com.client as win32
from win32com.client import constants
import pythoncom

from pyxllib.prog.newbie import RunOnlyOnce


def get_win32_app(name, visible=False):
    """ 启动可支持pywin32自动化处理的应用

    Args:
        str name: 应用名称，不区分大小写，比如word, excel, powerpoint, onenote
            不带'.'的情况下，会自动添加'.Application'的后缀
        visible: 应用是否可见

    Returns: app

    """
    # 1 name
    name = name.lower()
    if '.' not in name:
        name += '.application'

    # 2 app
    # 这里可能还有些问题，不同的应用，机制不太一样，后面再细化完善吧
    try:
        app = win32.GetActiveObject(f'{name}')  # 不能关联到普通方式打开的应用。但代码打开的应用都能找得到。
    except pythoncom.com_error:
        app = win32.gencache.EnsureDispatch(f'{name}')

    if visible is not None:
        app.Visible = visible

    return app


def __word():
    pass


def wd_save_format(name):
    """ word保存类型的枚举

    >>> app = get_win32_app('word')  # 要确保有app，才能获得常量值
    >>> wd_save_format('.html')
    8
    >>> wd_save_format('Pdf')
    17
    >>> wd_save_format('wdFormatFilteredHTML')
    10
    >>> app.Quit()
    """

    # common = {'doc': 0, 'html': 8, 'txt': 2, 'docx': 16, 'pdf': 17}
    common = {'doc': 'wdFormatDocument97',
              'html': 'wdFormatHTML',
              'txt': 'wdFormatText',
              'docx': 'wdFormatDocumentDefault',
              'pdf': 'wdFormatPDF'}

    name = common.get(name.lower().lstrip('.'), name)
    return getattr(constants, name)


class EnchantWin32WordApplication:
    pass


@RunOnlyOnce
def enchant_win32_word_application(ref_obj):
    """
    Args:
        ref_obj: 参考对象，需要从ref_obj来获得的动态生成的type(ref_obj)类类型
    """
    pass
