#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

 
#：python -m moofei.find 127.0.0.1:5000 --webbrowser
#：python find 127.0.0.1:5000 --webbrowser
    

import os, sys, time, re, json
import zipfile
from moofei.valid.flask_valid import *
from moofei.thread import Thread,is_threading_patch,sleep
from moofei._valid import VALID
from moofei._find import __find__, _parse_params, _py, isascii
try:
    from util import get_free_mem, split_kv, execfile
    from _cat import _cat
except:
    from moofei.util import get_free_mem, split_kv, execfile
    from moofei._cat import _cat

from flask import Flask, request, send_from_directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

intervalDict={}
prosDict = {}

def static_file(path="", is_static=True, is_zip=False, as_attachment=True): 
    if not path: path = 'find.html'
    if is_static:
        fpath = os.path.join(os.path.dirname(__file__),  'static', path)
        content = os.path.isfile(fpath) and open(fpath, 'rb').read() or ""
        return content
    else:
        fpath = path.replace('\\','/')
        if '/' in fpath:
            dirpath,filename = fpath.rsplit('/',1) 
        else:
            dirpath,filename = './', fpath 
        #print(path, os.path.isfile(path),as_attachment)
        # as_attachment=True 一定要写，不然会变成打开，而不是下载
        if os.path.isfile(path):
            from flask import Response
            if not as_attachment :
                return Response(open(path,'rb').read(), mimetype='text/txt')
            elif is_zip:
                backupdir = './.backup'
                if not os.path.isdir(backupdir): os.mkdir(backupdir)
                backupname = os.path.join(backupdir, 'temp.zip')
                zip = zipfile.ZipFile(backupname, 'w', zipfile.ZIP_DEFLATED)
                zip.write(path)
                zip.close()
                return Response(open(backupname,'rb').read(), mimetype='application/zip')
            
        return send_from_directory(dirpath, filename, as_attachment=as_attachment)

@valid.func(['path:str', 'page:int', 'bsize:int', 'words:','not_word:', 'pre_word:', 'fpath:', 'fname:', 'file:', 'curpage:int','encoding:' ])
def pageView(path, page, bsize, words='', not_word="", pre_word="", fpath="", fname="", file="", curpage=0, encoding=None):
    path = path or fpath or fname or file
    if path:
        if curpage: page=curpage-1
        elif not page: page=0
        data = _cat(path, page=page, bsize=bsize, words=words, not_word=not_word, pre_word=pre_word, encoding=encoding) 
        if data:
            txts, inlines = data
            rs = inlines[2]
            rs['curpage'] = rs['page']+1
            rs['path'] = path
            rs['txt'] = '\n'.join(txts)
            return rs
            
@valid.func(['interval:str'])
def infoPros(interval):
    if interval and interval in intervalDict:
        data = {'finish':intervalDict[interval]['finish'], 'pros':1} 
        if interval in prosDict:
            data['finish'] = 0 
    else:
        data = {'finish':0, 'pros':0} 
    return data    
    
@valid.func(['interval:str'])
def stopPros(interval):
    if interval and interval in intervalDict:
        intervalDict.pop(interval,{'finish':0})['finish'] = 1
        if is_threading_patch: sleep(0.05)
        prosDict[interval].kill()
        del prosDict[interval]
    return {'data':"OK"}     
               
@valid.func(['interval:str', 'name:str','words:trim;str','fcase:int','ftype:int','wcase:int', 'plugin_box:strs','plugin_fix:strs','show_only_file:int','basedir:str','isdeep:int', 'fsize:trim', 'istry:int','more_break:int','mass_words:trim;str' ])
def finds(interval, name='.', words="", fcase=1, ftype=None, wcase=0, plugin_box='', plugin_fix='', show_only_file=0, basedir="", isdeep=None, fsize=None, istry=0, more_break=1, mass_words="", **awgs):   
    if '.doc(x)' in plugin_fix: plugin_fix+=['.doc','.docx']
    if '.xls(x)' in plugin_fix: plugin_fix+=['.xls','.xlsx']
    if '.tar' in plugin_box: plugin_box+=['.tar.gz', '.tar.bz2', '.tar.xz']
    if not words: awgs.pop('rewords',None)  
    now = time.time() 
    
    if not ftype and (not name or name=='.') and (words or awgs.get('rewords')):
        ftype = 0
    else:
        ftype=(name in ('.','') and 2) or ftype or None
        
    dawgs = dict(
                    basedir = basedir or "./",
                    fsize = fsize,
                    isdeep = isdeep,
                    words = re.compile(words) if words and wcase==2 else words,
                    fcase = fcase, ftype=ftype,
                    wcase = wcase,
                    show_only_file = show_only_file,
                    is_read_fcall = 1 if words else 0,
                    compressed_magic_list = plugin_box or False,
                    plugin_box = plugin_box,
                    plugin_fix = plugin_fix,
                    isbox = True if plugin_box else False ,
                    istry = istry,
                    more_break = more_break,
                    #debug = 1,
                 )
    word_keys = None
    if  words: word_keys = [words]   
    if interval not in intervalDict:
        dawgs.update(awgs)
        dawgs.pop('prune', None)
        
        backupdir = dawgs.pop('backupdir',None) or './.backup'
        if mass_words.strip():
            mass_words = [e.strip() for e in mass_words.replace('\r', '\n').split('\n') if e.strip()]
            words = {}
            for e in mass_words:
                v = split_kv(e)
                if len(v)==1:
                    words[v[0]]=""
                else:
                    words[v[0]]=v[1]
            dawgs['rewords'] = True 
            dawgs['words'] = words
            word_keys = list(words.keys())    
            
        if words and dawgs.get('rewords') and dawgs.get('use_backup'):
            if not os.path.isdir(backupdir):
                os.mkdir(backupdir)
            backupname = backupdir+'/'+interval.replace(':','').replace(' ','')+'.zip'
            dawgs['backup_zipfile'] = zipfile.ZipFile(backupname, 'w', zipfile.ZIP_DEFLATED)
            dawgs['backup_zipfile_name'] = backupname
        if dawgs.get('is_downzip'):
            if not os.path.isdir(backupdir):
                os.mkdir(backupdir)
            backupname = backupdir+'/'+interval.replace(':','').replace(' ','')+'.down'+'.zip'
            dawgs['download_zipfile'] = zipfile.ZipFile(backupname, 'w', zipfile.ZIP_DEFLATED)
            dawgs['download_zipfile_name'] = backupname    
        if awgs.get('prune'):
            dawgs.setdefault('prune', []).append(backupdir)
            dawgs['ignores'] = ['.backup/',os.path.join(basedir,'.backup/')]
        if awgs.get('is_auto_prune'):
            dawgs.setdefault('prune', []).append('.')
        if awgs.get('isgit'):
            dawgs['files_list'] = [os.path.join(basedir,e.strip()) for e in os.popen('cd %s && git ls-files'%basedir).readlines()]
            dawgs['basedir'] = []
        if basedir and os.path.isfile(basedir):
            dawgs['files_list'] = ['',[basedir]]
            dawgs['basedir'] = []
        if dawgs.get('plugin_main') and not os.path.isfile(dawgs['plugin_main']):
            dawgs.pop('plugin_main', None) 
        if is_threading_patch and word_keys:
            print(interval, 'sleeping used.')    
            dawgs['sleep'] = sleep  
        #dawgs['bsize'] = get_free_mem()
        #dawgs['more_break'] = True
        try:
            _parse_params(name, **dawgs)
        except:
           return {'data':{'path': "", 'linecount':0,'filecount':0,  'word_keys':word_keys, 'total':0, 'result':[":::参数错误::::"], 'finish':1}} 
        
        data = {'path': "", 'linecount':0,'filecount':0,'total':0,
                'ctime':now, 'ntime':now,
                'word_keys':word_keys, 'result':[], 'finish':0}
        intervalDict[interval] = data
        pros = Thread(find_call, interval, name or '.', dawgs, data)
        prosDict[interval] = pros
        pros.start()
        print(interval, 'pros start......')
        
    if len(intervalDict)>1:
        for k in  list(intervalDict.keys()):
            if k == interval:
                pass
            elif now > intervalDict[k]['finish']>0:
                intervalDict.pop(k,None)
                del prosDict[k]
                #os.kill(pid, signal.SIGKILL)  # kill子进程
    if not intervalDict[interval]['finish'] and prosDict[interval].is_end:
        intervalDict[interval]['finish'] = 1
        intervalDict[interval]['result'].append('')
        iserror=prosDict[interval].is_error
        if iserror:
            intervalDict[interval]['result'].append(str(iserror))
        intervalDict[interval]['result'].append(":::::::::::::::::::: func error ::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    return {'data':intervalDict[interval], 'pros_num':len(prosDict)}

@valid.func(['strs:strs'])    
def str_join(strs):
    return ''.join(strs)
    
    
def find_call(interval, name, dawgs, data):
    def line_decode(line, encoding):
        if encoding in ('str','string'):
            pass
        else:
            if encoding=='utf-8' and line[:3] == b'\xef\xbb\xbf':
                encoding = 'utf-8-sig'
            line = line.decode(encoding or 'utf-8','ignore')
        return line.strip() 
        
    def wcall(*lst,**dct):
        if is_threading_patch: sleep(0)
        fpath = dct['fpath']
        frombox = dct['frombox']
        encoding = dct.get('encoding')
        data['linecount'] += 1
        
        if frombox:
            try:
                fpath = u'{0} -> {1}'.format(fpath, frombox)
            except UnicodeDecodeError:
                fpath = str_join([fpath, ' -> ', frombox]).decode('gbk')
                
        if fpath != data['path']:
            #fpath = VALID.isStr(fpath)[1] #???
            data['path'] = fpath
            data['filecount'] += 1
            data['result'].append("")
            data['result'].append(fpath)
            
        if is_threading_patch: sleep(0)    
        if dawgs.get('show_only_file'): return
        data['result'].append('line %s: '%(lst[1]+1))
        
        line = lst[0]
        if len(line) < 1024:
            line = line_decode(line,encoding)
        else:
            start,end = lst[2],lst[3]
            if end<1024:
                line_words,line_start = line_decode(line[:1024+512],encoding),""
            elif len(line)-end<1024:
                line_words,line_start = line_decode(line,encoding)[-1024:],""
            else:
                line = line_decode(line,encoding)
                line_words = line[-100:end] if end-start>100 else line[start:end]
                line_start = line[:512] if start>512 else line[:start]
            line = u"~~(large Line:{0}.{1})~~{2}.... {3}....".format(len(line),start, line_start, line_words)
        #line = VALID.isStr(line)[1]
        data['result'].append(line)
        if is_threading_patch: sleep(0.01)
        
    def fcall(fpath, *lst,**dct):
        frombox = dct.get('frombox')
        try:
            if frombox: fpath = u'{0} -> {1}'.format(fpath, frombox)
        except UnicodeDecodeError:
            if frombox: fpath = u'{0} -> {1}'.format(fpath.decode('gbk'), frombox)
        #fpath = VALID.isStr(fpath)[1]
        data['result'].append(fpath)
        data['filecount'] += 1
        if is_threading_patch: sleep(0.01)
        return True 
    if  dawgs.get('words'):
        dawgs['wcall'] = wcall
    else:
        dawgs['fcall'] = fcall
    
    cpath = dawgs['basedir']    
    if dawgs['basedir'] and dawgs['basedir'].startswith(('./','..')):
        cpath = os.path.join(os.getcwd(), dawgs['basedir'])
        data['result'].append(cpath)
        data['result'].append(":::::::::::::::::::: start ::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        data['result'].append("")
    
    for e in __find__(name, **dawgs):
        data['total'] += 1
        if is_threading_patch: sleep(0)
        if interval not in intervalDict: break
        if data['finish']: break
        
        if dawgs.get('plugin_main'):
            if e[0] is not False and e[0] is not None:
                plugin_kawgs = {'fname':e[1],
                                'fpath':os.path.join(cpath,  e[1][0] if isinstance(e[0],  (list,tuple)) else e[1] ) 
                               }
                #print(plugin_kawgs, os.path.isfile(plugin_kawgs['fpath']))               
                execfile(dawgs['plugin_main'],
                         globals = plugin_kawgs, 
                         locals = plugin_kawgs, 
                        )
        if dawgs.get('download_zipfile') and e[0]:
            dawgs['download_zipfile'].write(e[1])
        #    print(e)
        #print(interval)
        if is_threading_patch and data.get('word_keys'): sleep(0.01)
        if dawgs.get('more_break') and len(data['result']) > 60000: 
            print(interval, 'more break....')
            data['result'].append("")
            data['result'].append("::::: More Line :::::: Break ::::: Please Put Limit!!")
            break
            
        
    data['result'].append("")
    data['result'].append('::::::::::::::::::: %(linecount)d linecount ::::::::::: %(filecount)d filecount ::::::::::::::::::::::::::'%data)
    data['result'].append("")
    data['finish'] = time.time()+5
    
    if dawgs.get('backup_zipfile'):
        dawgs['backup_zipfile'].close()
        if not data['filecount']:
            os.remove(dawgs['backup_zipfile_name'])
    
    if dawgs.get('download_zipfile'):
        dawgs['download_zipfile'].close()
        data['download_path'] = dawgs['download_zipfile_name']
        
    print(interval, 'pros stoped......')
    
    
    
    
    