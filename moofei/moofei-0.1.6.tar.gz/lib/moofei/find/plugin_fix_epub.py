#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

import sys
import re
import warnings
from moofei._find import _py, _strtypes,_find_func,_search_func, _get_chardet_detect
try:
    from .cplugin_fix import _StringIO, StringIO, cPlugin_Fix
except (ImportError,ValueError):
    from cplugin_fix import _StringIO, StringIO, cPlugin_Fix


try:
    from ebooklib import epub
    #original_get_template = epub.EpubBook.get_template
    #def new_get_template(*args, **kwargs):
    #    return original_get_template(*args, **kwargs).encode(encoding='utf8')
    #epub.EpubBook.get_template = new_get_template    
except:
    warnings.warn('Please Import python-ebooklib TO pip')

    
class Plugin_Fix_Epub(cPlugin_Fix):
    def all_texts(self):
        book = epub.read_epub(self.fp)
        result = b''
        for id, _ in book.spine:
            item = book.get_item_with_id(id)
            #print(item.content)
            result = result + item.content + b'\n'    
        return result
        
    
        
        
