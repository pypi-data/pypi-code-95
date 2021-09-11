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
    from .cplugin_fix import _StringIO, StringIO, BytesIO, cPlugin_Fix
except (ImportError,ValueError):
    from cplugin_fix import _StringIO, StringIO, BytesIO, cPlugin_Fix
import email

try:
    from email import Header  #py2
except:
    from email import header as Header #py3

    
class Plugin_Fix_Eml(cPlugin_Fix):
    def decode_str(self, s):  # 字符编码转换
        value, charset = Header.decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value
    def result(self):
        fp = open(self.get_tempfile_or_path(), "r")
        results = []
        #texts = []
        msg = email.message_from_file(fp)
        tmpfp = BytesIO()
        
        #subject =  # 取信件头里的subject,　也就是主题
        subject = self.decode_str(msg.get("subject")).encode('utf-8')
        #dh = Header.decode_header(Header.Header(msg.get("subject")))
        #subject = dh[0][0].decode(dh[0][1]).encode('utf-8')
        tmpfp.write(subject)
        tmpfp.write(b'\n')
        
        for par in msg.walk(): # 循环信件中的每一个mime的数据块
            if not par.is_multipart(): # 这里要判断是否是multipart，是的话，里面的数据是无用的，至于为什么可以了解mime相关知识。
                name = par.get_param("name") #如果是附件，这里就会取出附件的文件名
                if name:#有附件
                    # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
                    #h = Header.Header(name)
                    #dh = Header.decode_header(h)
                    #fname = dh[0][0] #
                    #fname = dh[0][0].decode(dh[0][1])
                    #if fname[-2:]=='?=': fname=fname[:-2]
                    fname = self.decode_str(name)
                    text = fname.encode('gbk')
                    data = par.get_payload(decode=True) #　解码出附件数据，然后存储到文件中
                    #open(fname, 'wb').write(data) #注意一定要用wb来打开文件，因为附件一般都是二进制文件
                    results +=  self.find_chunk(fname, data)
                else:
                    text = par.get_payload(decode=True) # 解码出文本内容，直接输出来就可以了。
                    coding = par.get_content_charset()
                    text = text.decode(coding).encode('gbk')
                tmpfp.write(text)
                tmpfp.write(b'\n')
           
        results +=  self.find_chunk('-->--main---eml.html', tmpfp)
        return results 
        
    
        
        
