#!/usr/bin/python
# coding: utf-8
# editor: mufei(ypdh@qq.com tel:15712150708)
'''
牧飞 _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

__all__ = ['urlopen', 'urlparse', 'tldextract', 'BASE_DIR']

import sys, os, re, time, math
import ftplib
import chardet
py = list(sys.version_info)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if py[0]==2:
    #url, data=None, timeout=<object>, cafile=None, capath=None, cadefault=False, context=None
    from urllib2 import urlopen
    from urlparse import urlparse
else:
    #url, data=None, timeout=<object>, *, cafile=None, capath=None, cadefault=False, context=None
    from urllib.request import urlopen
    from urllib.parse import urlparse
    
    
try:
   import tldextract
except:
   tldextract = None
   
   
try:
    import psutil
except:
    psutil = None
    
    
def split_kv(s):
    s = s.strip()
    e = s.split()
    if s.count('"')==2:
        if s[0]==s[-1]=='"':
            v = [s[1:-1]]
        else:
            o=re.match(r'\"(.+)\"\s+(.+)$', s)
            if not o:
                o=re.match(r'(.+)\s+\"(.+)\"$', s)
            if o:
                v = list(o.groups())
            else:
                v = e 
    elif s.count('"')==4:
        o=re.match(r'\"(.+)\"\s+\"(.+)\"$', s)
        if o:
            v = list(o.groups())
        else:
            v = e 
    else:
        v = e
    
    return v
    
def get_array_format_list(array, jump_empty=True):
    '''
    {code:str}{side_number:for(|A|B)}{cols:for(1,2)}{rows:for(2)}-{ex:for}
    [[fill,list],[fill,list]...]
    '''
    Ls = []
    length = len(array)
    for i in range(length):
        fill, lst = array[i]
        if jump_empty and not lst: continue
        L = ['%s%s'%(fill, e) for e in lst]
        if not Ls:
            Ls = L 
        else:
            Ls = ['%s%s'%(b,a) for a in L for b in Ls]
    return Ls

def IpToInt(ip):
    L = [int(e) for e in ip.strip().split('.')]
    ip_int = L[0]*256**3+L[1]*256**2+L[2]*256+L[3]
    return ip_int
    
def jinja2_render(fp, params):
    from jinja2 import Template
    if not isinstance(fp, str):
        fp = fp.read()
    if isinstance(fp, bytes):
        codingDict = chardet.detect(fp[:1024*100]) #many time to check ????  
        if codingDict['confidence'] < 0.5:
            encoding = 'GB18030'
        else:
            encoding = codingDict['encoding']
        print(encoding)
        if 'utf8' not in  encoding.lower().replace('-',''):
            fp=fp.encode(encoding)
        fp=fp.decode('utf-8')
            
    return Template(fp).render(**params)
        

class get_logfile:
    "every day write log"
    is_auto = True
    #__slots__ = ('baseFilename', 'mode', 'suffix','tm_mday', '_file')
    def __init__(self, baseFilename='./', mode='a', *args, **awgs):
        self.baseFilename = baseFilename
        self.mode = mode
        self.suffix = '%Y%m%d'
        self._file = None
        self.tm_mday = 0
        self.args = args
        self.awgs = awgs    
    def set_auto(self, is_auto = True):
        self.is_auto = is_auto
        return self    
    @property
    def file(self):    
        tm = time.localtime()
        mday = tm.tm_mday
        if mday!=self.tm_mday:
            if self._file: self._file.close()
            if os.path.isdir(self.baseFilename):
                fileName = os.path.join(self.baseFilename, time.strftime(self.suffix, tm))
            else:    
                dirName, baseName = os.path.split(self.baseFilename)
                fileName = self.baseFilename + "." + time.strftime(self.suffix, tm)
            self._file = open(fileName, self.mode, *self.args, **self.awgs)
            self.tm_mday = mday
        return self._file
    def write(self, line, *args, **kwargs):
        if self.is_auto or self._file is None:
            self.file.write(line)
        else:
            self._file.write(line)        
    def close(self):
        if self._file: self._file.close()
    def log(self): pass
    def flush(self, refresh=False):
        if self._file: 
            self._file.flush()
            if refresh: self.file
    def writelines(self, *args, **kwargs):
        for line in args: self.write(line)
    def __del__(self):
        self.close()
        
        
def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)
        
    
def get_free_mem():
    if psutil:
        return psutil.virtual_memory().free
        
    if os.path.isfile('/proc/meminfo'):
        mem = {}
        f = open('/proc/meminfo')
        lines = f.readlines()
        f.close()
        for line in lines:
            name = line.split(':')[0]
            var = line.split(':')[1].split()[0]
            mem[name] = float(var)
        return (mem['MemFree'] + mem['Buffers'] + mem['Cached']) * 1024
                
if __name__ == "__main__":
    print(get_free_mem())
    print(get_array_format_list([['0',[1,2,3]],['',['a','b','c']],[0,[]],['~','-+=*&']]))    


   
  