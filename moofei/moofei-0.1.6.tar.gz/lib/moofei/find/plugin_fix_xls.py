#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

    
try:
    from .plugin_fix_xlsx import Plugin_Fix_Xlsx
except (ImportError,ValueError):
    from plugin_fix_xlsx import Plugin_Fix_Xlsx   


class Plugin_Fix_Xls(Plugin_Fix_Xlsx):
    pass
    
        
    
        
