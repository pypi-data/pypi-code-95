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

import time
import zipfile 




class MemberInfo:
    def __init__(self, member):
        self.member = member
    def isdir(self):
        return False
        
    @property    
    def mtime(self):
        d = self.member.date_time
        gettime = "%s/%s/%s %s:%s:%s" % (d[0], d[1], d[2], d[3], d[4], d[5])
        return time.mktime(time.strptime(gettime, '%Y/%m/%d %H:%M:%S')) 
        
    @property        
    def name(self):  
        return self.member.filename
    @property        
    def size(self):  
        return self.member.file_size

        
class Plugin_Box_Zip:
    def __init__(self, fpath):
        self.fpath = fpath
        self.zf = zipfile.ZipFile(fpath,'r') # mode must be 'r'
        #print(help(self.zf))
        #print(fpath)
            
    def getmembers(self):
        for member in self.zf.filelist: #for f2 in zf.namelist():
            if (member.flag_bits & 0x01): continue #Encrypted file
            yield MemberInfo(member)
            
            
    __iter__ = getmembers 
    
    def extractfile(self, name, mode='r', pwd=None):
        return self.zf.open(name)
    
    def close(self):
        self.zf.close()
    def __enter__(self):
       return self.zf 
    def __exit__(self, *args, **awgs):
       self.zf.close()
       
       
       