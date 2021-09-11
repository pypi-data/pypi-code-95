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
from moofei._find import _py,_target_read_yield #, bcolors


import datetime
import time
try:
    from io import BytesIO
except:
    from cStringIO import StringIO as BytesIO 
    
#import archive
#import cabarchive 
     
try:
    import cabarchive
except ImportError:
    warnings.warn('Please Import python-cabarchive  TO pip')
    
class MemberInfo:
    def __init__(self, member):
        self.member = member
    def isdir(self):
        return False
        
    @property    
    def mtime(self):
        _p =  '%Y-%m-%d %H:%M:%S'
        e = str(self.member.date) + ' '+ str(self.member.time)
        return time.mktime(time.strptime(str(datetime.datetime.strptime(e.strip(), _p)), _p))
        
    @property        
    def name(self):  
        return self.member.filename
    @property        
    def size(self):  
        return len(self.member) 

    
    
class Plugin_Box_Cab:
    def __init__(self, fpath):
        self.fpath = fpath
        self.zf = cabarchive.CabArchive()
        with open(fpath, "rb") as f:
            buf = f.read()

        # parse cabinet, repeating until all the checksums are fixed
        while True:
            try:
                self.zf.parse(buf)
                break
            except cabarchive.CorruptionError as e:
                offset = e[1]
                buf = buf[:offset] + struct.pack("<I", e[3]) + buf[offset + 4 :]
            except cabarchive.errors.NotSupportedError as e:
                #like reason for dir errors
                raise
        
    def getmembers(self):
        for name in  self.zf:
            yield MemberInfo(self.zf[name])
                    
    __iter__ = getmembers
    def extractfile(self, name, *args,**awgs):
        return BytesIO(self.zf[name].buf)
        
    def close(self):
        pass
    def __enter__(self):
       return self.zf 
    def __exit__(self, *args, **awgs):
       pass

    