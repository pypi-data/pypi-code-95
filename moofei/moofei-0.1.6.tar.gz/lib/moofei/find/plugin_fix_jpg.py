#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

#openocr
#tesseract-ocr
#PaddleOCR
#cnocr cnstd 
#chineseocr



from moofei._find import _py, _strtypes,_find_func,_search_func
try:
    from .plugin_fix_image import cPlugin_Fix_Image
except (ImportError,ValueError):
    from plugin_fix_image import cPlugin_Fix_Image


class Plugin_Fix_Jpg(cPlugin_Fix_Image):
    pass
        
