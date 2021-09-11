#!/usr/bin/python
# coding: utf-8
# editor: mufei(ypdh@qq.com tel:15712150708)
'''
牧飞 _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

__all__ = ['get_apnic', 'readIpTxt', 'IPList']

import sys, os, re, math, ftplib
from moofei.util import BASE_DIR, IpToInt
from moofei._valid import VALID

def readTxt(path):
    if not os.path.isfile(path):
        return []
    with open(path,'r') as f:
        txt = f.read()
    txt = re.sub(r'<!--[\s\S]*?-->', ' ', txt)
    L = []
    for line in txt.split('\n'):
        s = line.split('#')[0].strip()
        if s: L.append(s)
    return L

int_ip = lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)])
ip_int = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
def readIpTxt(path, ipList=None):
    '''
    >>> o = readIpTxt(os.path.join(BASE_DIR, 'static', 'local.ip'))
    >>> len(o), '100.100.0.100' in o
    (45, True)
    '''
    L = readTxt(path)
    if ipList is None: ipList = IPList()
    if not L: return ipList
    
    for s in L:
        if s[0]=='(' and s[-1]==')': s=s[1:-1].strip()
        s = s.replace(',','|')
        if '|' in s:
            ss = s.split('|')
        else:
            ss = [s]
        for e in ss:
            ipList.add(e)
            
    return ipList


    
def get_apnic(fpath=None, to_int=False):
    '''
    >>> len(get_apnic('./apnic.tmp')); os.remove('./apnic.tmp')
    46894
    '''
    #   http://www.apnic.net/db/rir-stats-format.html
    # or
    #	ftp://ftp.apnic.net/pub/apnic/stats/apnic/README.TXT
    #
    # (from) http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest
    fpath =  fpath or  os.path.join(BASE_DIR, 'static', 'delegated-apnic-latest.txt')
    if not os.path.isfile(fpath) or os.stat(fpath).st_size<1000:
        apnicip = ftplib.FTP('ftp.apnic.net')
        apnicip.login()
        apnicip.cwd('/public/apnic/stats/apnic')
        ipfile = open(fpath, 'wb')
        apnicip.retrbinary('RETR delegated-apnic-latest', ipfile.write)
        ipfile.close()

    Ls = []
    with open(fpath, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith(('$','#')): continue
            ss = line.split('|')
            if len(ss)<5: continue
            if ss[2] != 'ipv4': continue
            
            ip = ss[3]
            country = ss[1]
            if to_int:
                if ip=='*': ip='0.0.0.0'
                ip0 = IpToInt(ip)
                ip1 = ip0 + int(ss[4]) - 1
                Ls.append((ip0, ip1, country))
            else:
                mask=str(int(32 - math.log(int(ss[4]), 2)))
                Ls.append((ip, mask, country))
    return Ls        
              
class IPList(object):
    def __init__(self, path=None): 
        self.__list = set()
        self.__list6 = set()
        self.path = path
        if self.path:
            readIpTxt(path, self)
        
    def __nonzero__(self):
        return self.__list or self.__list6
    def __len__(self):
        return len(self.__list) + len(self.__list6)
        
        
    def clear(self):
        self.__list.clear()
        self.__list6.clear()
    def update(self, lst):
        if isinstance(lst, IPList):
            self.__list.update(lst._get_ipv4())
            self.__list6.update(lst._get_ipv6())
        elif isinstance(lst, (tuple,list, set)):
            for ip in lst:
                self.add(ip)
    def reload(self, path=None):
        self.clear()
        readIpTxt(path or self.path, self)
        
    def _get_ipv4(self): return self.__list
    def _get_ipv6(self): return self.__list6    
        
    def __contains__(self, ip):
        if isinstance (ip,str) and  ':' in ip:
            L  = self.__list6
            state, ips = VALID.isIpv6range(ip)
        else:
            state, ips = VALID.isIpv4range(ip)
            L  = self.__list
        if state<1:
            return False
         
        for k in L:
            if k[1]>=ips[1] and k[0]<=ips[0]:
                return True
        return False

    def add(self, ip):
        from moofei._valid import VALID
        if isinstance (ip,str) and  ':' in ip:
            v = 6
            state, ips = VALID.isIpv6range(ip)
        else:
            state, ips = VALID.isIpv4range(ip)
            v = 4
            
        if state<1:
            return False
            
        if v==4:
            self.__list.add(tuple(ips))
        else:
            self.__list6.add(tuple(ips))        
        return True
    append = add        
                
    def json(self):
        return {'ipv4':self.__list, 'ipv6':self.__list6}  

        
if __name__ == "__main__":
    import doctest
    doctest.testmod() #verbose=True
   
  