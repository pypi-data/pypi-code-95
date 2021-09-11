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
from moofei._find import _py

try:
    import rarfile 
except ImportError:
    if _py[0]==2: 
        warnings.warn('Please Import rarfile==3.1  TO pip')    
    else: 
        warnings.warn('Please Import rarfile TO pip')
except NameError:
    if _py[0]==2: 
        warnings.warn('Please Import rarfile==3.1  TO pip')    
    else: 
        warnings.warn('Please Import rarfile TO pip')

#Copy [unrar.exe of winrar] To [venv/Scripts]
#sys.path.append(r'C:\Program Files\WinRAR') [useless] (Must be added under scripts)





                
class Plugin_Box_Rar:
    def __init__(self, fpath):
        self.fpath = fpath
        self.zf = rarfile.RarFile(fpath, mode='r') # mode must be 'r'
        #print(help(self.zf))
            
    def getmembers(self):
        if not self.zf.needs_password():
            for member in  self.zf.infolist():
                member.name = member.filename
                member.size = member.file_size
                #print(help(member))
                yield member
            
            
    __iter__ = getmembers 
    
    def extractfile(self, name, mode='r', pwd=None):
        return self.zf.open(name, mode=mode)
    
    def close(self):
        self.zf.close()
    def __enter__(self):
       return self.zf 
    def __exit__(self, *args, **awgs):
       self.zf.close()
       
       
       