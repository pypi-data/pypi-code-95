#!/usr/bin/python
# -*- coding: UTF-8 -*-
# editor: moofei
'''
ypdh@qq.com: Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''
__all__  = ['Php']

import os,sys,time,re,base64
import datetime
from collections import OrderedDict as __OrderedDict
import types
import copy
import functools
import hashlib
from string import Template  as string_Template
import urllib
import traceback
import logging
import shutil
#pip install var_dump

true = True
false = False

from socket import inet_aton
from struct import unpack

true = True
false = False
try:
    basestring
except NameError:
    basestring = str
    
try:
    long
except NameError:
    long = int
    
py = list(sys.version_info)    
def is_string(L): return isinstance(L, basestring)
def is_array(L): return isinstance(L, (tuple,list))


def Dsort(d):
    if isinstance(d,dict):
        _d = __OrderedDict()
        keys = sorted(d.keys())
        for k in keys:
            _d[k] = Dsort(d[k])
        return _d
    elif isinstance(d,list): 
        _d = []
        for k in d:
            _d.append(Dsort(k))
        return _d
    else:
        return d

class Php:
    class array:
        __type__ = 'array'
        #array('1',array('gt','0'),'thinkphp','_multi'=>true);
        def __init__(self, *args, **awgs):
            self.args = args
            self.awgs = awgs or {}
        def keys(self):
            return list(self.args)+list(self.awgs.keys())
        def get(self, key, value=None):
            return self.awgs.get(key, value)
        def __contains__(self, key): return key in self.awgs
        def __delitem__(self, key): del self.awgs[key]
        def pop(self, k):
            if k in self.awgs: del self.awgs[k]
            elif k in self.args: self.args.remove(k)
        def __len__(self): return len(self.args)+len(self.awgs)
        def __iter__(self): return iter(self.items())
        def items(self):
            d = {}
            for i in range(len(self.args)):
                d[i] = self.args[i]
            d.update(self.awgs)
            return d.items()
        def __setitem__(self, key, value): self.awgs[key]=value
        def __getitem__(self, key):
            if key in self.awgs: return self.awgs[k]
            if type(key)==types.IntType and len(self.args)>key:
                return self.args[key]
        def append(self, key):
            self.args.append(key)
        
    @staticmethod
    def is_array(L): 
        '''
        >>> array = Php.array('1',Php.array('gt','0'),'thinkphp', _multi=true); Php.is_array(array)
        True
        '''
        return is_array(L) or getattr(L, '__type__', None)=='array'
    
    @staticmethod
    def is_arrays(L): 
        return is_array(L) or getattr(L, '__type__', None)=='array'

    @staticmethod
    def array_merge(d, *args):
        '''
        >>> d=Php.array_merge({2:1,3:2}, {2:2,1:0}, {3:3}); Dsort(d)
        OrderedDict([(1, 0), (2, 2), (3, 3)])
        '''
        for e in args: d.update(e)
        return d
    
    @staticmethod
    def array_diff(L, *Ls):
        '''
        >>> d= Php.array_diff({1:2,2:3,3:4,5:6}, {1:0}, {2:3}); Dsort(d)
        OrderedDict([(3, 4), (5, 6)])
        '''
        for e in list(L.keys()):
            for Li in Ls:
                if e in Li:
                    L.pop(e); break
        return L
        
    @staticmethod 
    def strpos(s, p):
        '''
        >>> Php.strpos('012345', '1')
        True
        '''
        return p in s
        
    @staticmethod
    def substr(s, sat, end=None): 
        '''
        >>> Php.substr('0123456', 2, 4)
        '2345'
        '''
        return s[sat:] if end is None else s[sat:(sat+end if end>0 else end)]
        
    @staticmethod
    def implode(dot, L=None):
        '''
        >>> Php.implode(',', ["1","2"])
        '1,2'
        '''
        if L is None: dot, L = ',', dot
        if isinstance(L, dict):
            L=L.keys()
        return dot.join(L)
        
    @staticmethod 
    def addslashes(s):
        '''
        >>> Php.addslashes("'\\seee")
        "\\\\'\\\\\\\\seee"
        '''
        d = {'"':'\\"', "'":"\\'", "\0":"\\\0", "\\":"\\\\"}
        return ''.join(d.get(c, c) for c in s)
        
    @staticmethod 
    def is_scalar(s):
        '''
        >>> Php.is_scalar(None)
        True
        '''
        return s in (false, true, None) or isinstance(s,(basestring, int, float, long))
        
        
    @staticmethod 
    def parse_str(s, d=None):
        '''
        >>> d=Php.parse_str("first=value&arr[]=foo+bar&arr[]=baz"); Dsort(d)
        OrderedDict([('arr', ['foo bar', 'baz']), ('first', 'value')])
        '''
        if d is None: d={}
        if py[0]==2:
            from cgi import parse_qs
        else:
            from urllib.parse import parse_qs
        di = parse_qs(s)
        for k,v in di.items():
            if k.endswith('[]'): d[k[:-2]] = v 
            else:
                d[k]=v[0]
        return d
    
    @staticmethod 
    def array_walk(d, fn, *args):
        '''
        >>> def fn(s, *args): return s+1 
        >>> d=Php.array_walk({1:2,2:3}, fn, 3); Dsort(d)
        OrderedDict([(1, 3), (2, 4)])
        '''
        if is_array(d): dx = [fn(d[k], *args) for k in d]
        else:
            dx = {} 
            for k in d: dx[k] = fn(d[k], *args)
        return dx
    
    @staticmethod 
    def array_shift(L):
        '''
        >>> Php.array_shift([2,3,4,5])
        2
        '''
        r = L[0]
        L[:] = L[1:]
        return r
    
    @staticmethod 
    def strtolower(s):
        '''
        >>> Php.strtolower('AsAA A')
        'asaa a'
        '''
        return s.lower()
    
    @staticmethod 
    def strtoupper(s): 
        '''
        >>> Php.strtoupper('AsAA a')
        'ASAA A'
        '''
        return s.upper()
    
    @staticmethod 
    def trim(s, m=None): 
        '''
        >>> Php.trim(' s s  ')
        's s'
        '''
        return s.strip(m) if m else s.strip()
    
    @staticmethod 
    def is_numeric(s, stp=''):
        '''
        >>> Php.is_numeric(455)
        True
        '''
        if isinstance(s,(int, long, float)): return True 
        if isinstance(s,basestring) and re.match(r'[+-]?\d+$', s):return true
        return false
        
    @staticmethod 
    def round(s):
        '''
        >>> Php.round('4')
        4
        '''
        return int(s) if Php.is_numeric(s) else 0

    @staticmethod
    def md5(s):
        '''
        >>> Php.md5('xxxxx5')
        '4ad6744884ad218aad9d4b646ba0dee1'
        '''
        if py[0]==2:
            m = hashlib.md5()
            m.update(bytes(s))
        else:
            m = hashlib.md5()
            m.update(bytes(s, encoding='utf-8'))
        return m.hexdigest()

    @staticmethod
    def date(format='%m/%d/%Y %H:%M', timestamp=None):
        '''
        >>> Php.date('Ymd', 1611298655)
        '20210122'
        '''
        ms = "YmdHMS"
        if '%' not in format: format = ''.join(['%'+e if e in ms else e for e in format.replace('i', 'M').replace('s', 'S')])
        d = datetime.datetime.fromtimestamp(timestamp or time.time())
        return d.strftime(format)
        
    @staticmethod 
    def str_replace(klst, vlst, s=None): #??????????????????????????????
        #'用一个数据替换另一个数据'
        '''
         
        '''
        if is_array(klst) and is_array(vlst): replace_dict = dict(zip(klst, vlst))
        elif type(klst)==types.DictType and is_string(vlst): replace_dict, s = klst, vlst
        return multiple_replace(replace_dict, s)
    
    @staticmethod 
    def preg_replace(pattern , replacement, subject, limit=0):
        '''
        >>> Php.preg_replace(r'\d', '+', "55dddtteee666", limit=3)
        '++dddtteee+66'
        '''
        if limit:
            result = re.sub(pattern, replacement, subject, limit)
        else:
            result = re.sub(pattern, replacement, subject)
        return result

    @staticmethod 
    def foreach(data): #new
        '''
        >>> o=Php.foreach([1,2,3]);  list(o)
        [(0, 1), (1, 2), (2, 3)]
        '''
        if isinstance(data, dict):
            return data.items()
        elif is_array(data):
            return enumerate(data)
        elif getattr(data, '__type__', None)=='array':
            return data.items()
        return data
    #items = foreach
    
    @staticmethod 
    def preg_replace_callback(rex, callback, strings):
        '''
        >>> def callback(m): return '~'+m.group()
        >>> Php.preg_replace_callback(r"\d", callback, '55fdd-afafa66' )
        '~5~5fdd-afafa~6~6'
        '''
        if is_string(strings):
            return re.sub(rex, callback, strings)
        else:
            return [re.sub(rex, callback, e) for e in strings]

    @staticmethod
    def preg_match(pattern, subject, flags=None):
        '''pattern: 可以去掉前后俩个/ 
        >>> Php.preg_match('\d', '555ffff').group()
        '5'
        '''
        if flags:
            matches = re.search(pattern, subject, flags)
        else:
            matches = re.search(pattern, subject)
        return matches

        
    @staticmethod         
    def ucfirst(s):
        '''
        >>> Php.ucfirst('sCCCiii00-oouu')
        'Sccciii00-oouu'
        '''
        return s.capitalize()

    # global, str_repeat
    @staticmethod
    def str_repeat(the_str, multiplier):
        '''
        >>> Php.str_repeat('*',5)
        '*****'
        '''
        return the_str * multiplier


    @staticmethod
    def mcrypt_encrypt(cipher, key, data, mode=None, iv=None):#PHP 4 >= 4.0.2, PHP 5
        #"cipher: DES|AES"
        """AES_key: It must be 16 (*AES-128*), 24 (*AES-192*), or 32 (*AES-256*) bytes long
           mode=AES.MODE_CBC:输入的加密字符必须是16的倍数，php的默认补零，所以解密的时候还需要rtrim掉零。
        >>> s=Php.mcrypt_encrypt('DES', b'12345678', b'12345adaffafeee6'); str(base64.b32encode(s).decode())
        'DOZME345SFPUI433R2CATVKSSQ======'
        >>> s=Php.mcrypt_encrypt('AES', b'12345678', b'12345adaffafeee6'); str(base64.b32encode(s).decode())
        'RSUK4WPA5DWHBT3YVMKMVGTTAM======'
        """
        #for DES3
        padding = b'\0'
        if cipher.upper() in ('MCRYPT_DES', 'DES'):
            from Crypto.Cipher import DES as  m_cipher #require pycrypto  MODE_CBC
            mode = mode or m_cipher.MODE_ECB #8位 
            #if len(key)<16: key = key.ljust(16, padding)
                
        elif cipher.upper() in ('MCRYPT_AES', 'AES'):
            #AES key must be either 16, 24, or 32 bytes long #default : MODE_ECB 
            from Crypto.Cipher import AES as  m_cipher #require pycrypto 
            if len(key)<16: key = key.ljust(16, padding)
            mode = mode or m_cipher.MODE_ECB #8位
            
        #AES.key_size=128
        if iv:
            crypto = m_cipher.new(key=key, mode=mode, IV=iv) #MODE_CBC
        elif mode:
            crypto = m_cipher.new(key=key, mode=mode) #MODE_ECB
        else:
            crypto = m_cipher.new(key=key)

        #size = crypto.block_size
        size = getattr(crypto, 'block_size', None)
        if size:
            length = len(data) #data.count('')-1
            if length%size: #size=8
                data += padding*(size-length%size)
                
        #txt = base64.b64decode(data) # your ecrypted and encoded text goes here
        origin = crypto.encrypt(data)
        return origin

    @staticmethod
    def mcrypt_decrypt(cipher, key, data, mode=None, iv=None):#PHP 4 >= 4.0.2, PHP 5
        """cipher: DES|AES
        >>> s=Php.mcrypt_decrypt('DES', b'12345678', base64.b32decode('DOZME345SFPUI433R2CATVKSSQ======')); str(s.decode())
        '12345adaffafeee6'
        >>> s=Php.mcrypt_decrypt('AES', b'12345678', base64.b32decode('RSUK4WPA5DWHBT3YVMKMVGTTAM======')); str(s.decode())
        '12345adaffafeee6'
        """
        #for DES3
        padding = b'\0'
        if cipher.upper() in ('MCRYPT_DES', 'DES'):
            from Crypto.Cipher import DES as  m_cipher #require pycrypto
            mode = mode or m_cipher.MODE_ECB
        elif cipher.upper() in ('MCRYPT_AES', 'AES'):
            from Crypto.Cipher import AES as  m_cipher #require pycrypto
            if len(key)<16: key = key.ljust(16, padding)
            mode = mode or m_cipher.MODE_ECB #8位
        #AES.key_size=128
        if iv:
            crypto = m_cipher.new(key=key, mode=mode, IV=iv)
        elif mode:
            crypto = m_cipher.new(key=key, mode=mode)
        else:
            crypto = m_cipher.new(key=key)

        #txt = base64.b64decode(data) # your ecrypted and encoded text goes here
        origin = crypto.decrypt(data)
        return origin #.rstrip("\0")
    
    @staticmethod    
    def unserialize(s): return phpserialize.unserialize(s)

    @staticmethod
    def serialize(s): return phpserialize.serialize(s)
    
    @staticmethod
    def base64_encode(s):
        '''
        >>> str(Php.base64_encode('哎呀呀呀').decode()).strip()
        '5ZOO5ZGA5ZGA5ZGA'
        '''
        if py[0]==2: #Python 2.x:
            result = s.encode('base64')
        else:
            if isinstance(s, str): s = s.encode()
            result = base64.encodestring(s) #python 3.x
        return result
    
    @staticmethod
    def urlencode(s):
        '''
        >>> s=Php.urlencode('www.aliyun.com/?s=我&m=ww'); s
        'www.aliyun.com%2F%3Fs%3D%E6%88%91%26m%3Dww'
        '''
        if py[0]==2:
            result = urllib.quote_plus(s) # #2.x
        else:
            #import urllib.parse #3.x
            result = urllib.parse.quote_plus(s) 
        return result
    
    @staticmethod
    def strip_tags(html, allow_tags=None, allow_attrs=None):
        '''
        >>> Php.strip_tags('<html><a>xxx</a><div>kkkk</div></html>')
        'xxxkkkk'
        '''
        try:
            from html.parser import HTMLParser
        except:
            from HTMLParser  import HTMLParser
        result = []
        start = []
        data = []
        # 特殊的自闭和标签, 按 HTML5 的规则, 如 <br> <img> <wbr> 不再使用 /> 结尾
        special_end_tags = [
            'area', 'base', 'br', 'col', 'embed', 'hr',
            'img', 'input', 'keygen', 'link', 'meta', 'param',
            'source', 'track', 'wbr'
        ]
     
        def starttag(tag, attrs):
            if tag not in allow_tags:
                return
            start.append(tag)
            my_attrs = []
            if attrs:
                for attr in attrs:
                    if allow_attrs and attr[0] not in allow_attrs:
                        continue
                    my_attrs.append(attr[0] + '="' + attr[1] + '"')
                if my_attrs:
                    my_attrs = ' ' + (' '.join(my_attrs))
                else:
                    my_attrs = ''
            else:
                my_attrs = ''
     
            result.append('<' + tag + my_attrs + '>')
     
        def endtag(tag):
            if start and tag == start[len(start) - 1]:
                # 特殊自闭和标签按照HTML5规则不加反斜杠直接尖括号结尾
                if tag not in special_end_tags:
                    result.append('</' + tag + '>')
     
        parser = HTMLParser()
        parser.handle_data = result.append
        if allow_tags:
            parser.handle_starttag = starttag
            parser.handle_endtag = endtag
        parser.feed(html)
        parser.close()
     
        for i in range(0, len(result)):
            tmp = result[i].rstrip('\n')
            tmp = tmp.lstrip('\n')
            if tmp:
                data.append(tmp)
     
        return ''.join(data)

    @staticmethod
    def mb_detect_encoding(text, encoding_list=['ascii',"UTF-8","GB2312","GBK"], T=False):
        '''Return first matched encoding in encoding_list, otherwise return None.
        See [url]http://docs.python.org/2/howto/unicode.html#the-unicode-type[/url] for more info.
        See [url]http://docs.python.org/2/library/codecs.html#standard-encodings[/url] for encodings.
        >>> s=Php.mb_detect_encoding('我是谁')
        >>> s
        'UTF-8'
        '''
        #https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
        #另外: zip压缩的文件有字符编码的问题,比如linux下面压缩文件默认用utf-8,windows下面好像是GBK
               #所以你在windows下压缩的文件,需要用对应的编码方式来解压缩  不然会报错
        
        for best_enc in encoding_list:
            try:
                if py[0]==2:
                    unicode(text, best_enc)
                else:
                    text.encode(best_enc)
                #break    
            except:
                best_enc = None
            else:
                break
        if T:
            text = text if isinstance(text, unicode) else text.decode(best_enc, 'ignore') #GBK
            return text
        return best_enc
        
    @staticmethod 
    def parse_name(name, type=0) :
        def U(match): return Php.strtoupper(match[1])
        if type:
            return Php.ucfirst(Php.preg_replace_callback(r'/_([a-zA-Z])/', U, name))
        else :
            return Php.strtolower(Php.trim(Php.preg_replace(r"/[A-Z]/", r"_\\0", name), "_"))
    
if __name__ == "__main__":  
    import doctest
    doctest.testmod() #verbose=True    
