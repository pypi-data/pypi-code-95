#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''
#https://pypi.org/project/py7zr/

import sys
import re
import warnings
from moofei._find import _py,_target_read_yield

try:
    import py7zr 
except ImportError:
    if _py[0]==2: 
        warnings.warn('Please Import py7zr  TO pip')    
    else: 
        warnings.warn('Please Import py7zr TO pip')
except NameError:
    if _py[0]==2: 
        warnings.warn('Please Import py7zr  TO pip')    
    else: 
        warnings.warn('Please Import py7zr TO pip')


class MemberInfo:
    def __init__(self, member):
        self.member = member
    def isdir(self):
        return self.member.is_directory
    @property    
    def mtime(self):
        return self.member.creationtime.timestamp()
    @property        
    def name(self):  
        return self.member.filename
    @property        
    def size(self):  
        return self.member.uncompressed #compressed
        
class Plugin_Box_7Z:
    def __init__(self, fpath):
        self.fpath = fpath
        self.zf = py7zr.SevenZipFile(fpath,'r')
        #print(help(self.zf))
        
    def getmembers(self):
        if not self.zf.needs_password():
            for member in  self.zf.list():
                yield MemberInfo(member)
                    
    __iter__ = getmembers
    def extractfile(self, name, *args,**awgs):
        return self.zf.read(name, *args ,**awgs)[name]
        
    def close(self):
        self.zf.close()
    def __enter__(self):
       return self.zf 
    def __exit__(self, *args, **awgs):
       self.zf.close()
       
       
       