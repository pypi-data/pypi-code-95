#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''
#pip install python-docx
#https://python-docx.readthedocs.io/en/latest/

import warnings

try:
    from docx import Document
except ImportError:
    warnings.warn('Please Import python-docx TO pip')
    Document = None
    
try:
    from .cplugin_fix import _StringIO, StringIO, cPlugin_Fix
except (ImportError,ValueError):
    from cplugin_fix import _StringIO, StringIO, cPlugin_Fix       
from moofei._find import _strtypes,_find_func,_search_func

class Plugin_Fix_Odt(cPlugin_Fix):     
    def all_texts(self):
        if Document is None: 
            return self.word2txt()
        else:
            document = Document(self.fp)
            Ls = []
            for paragraph in document.paragraphs:
                Ls.append(paragraph.text)
            return '\n'.join(Ls)
        
        
