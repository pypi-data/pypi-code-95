#!/usr/bin/python
# coding: utf-8
# editor: mufei(ypdh@qq.com tel:15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

__all__ = ['_cat', ]

import sys,os,json,re,time,math
import chardet
py = list(sys.version_info)

def _cat(fname, page=None, bsize=100*1024, mode='rb', encoding=None, words=None, callback=None, **awgs):
    _words = words
    
    st_size = os.stat(fname).st_size
    if not st_size: return
    if not bsize: bsize = 100*1024
    txts = []
    n = 0
    if awgs.get('show_all'):
        seek_size = 0
    elif page is None:
        curpage = awgs.get('curpage')
        if isinstance(curpage, int) and awgs['curpage']>0:
            page = awgs['curpage']-1 
        else:
            page = int(st_size/bsize)
        seek_size = page*bsize
        if seek_size==st_size:
            page = int(st_size/bsize)-1
            seek_size = page*bsize
        if words and curpage is None:
            seek_size = 0
            page = 0
    elif page<0:
        seek_size = st_size+page*bsize
    else:
        seek_size = page*bsize
    if seek_size<0: seek_size=0
    elif seek_size>st_size: 
        seek_size = int(st_size/bsize)*bsize
    
    if words: mode = 'r'
    if py[0]==2 or 'b' in mode:
        fp = open(fname,mode)
    else:
        fp = open(fname,mode, encoding=encoding or 'utf-8')
        
    if words:
        fp.seek(seek_size)
        
        prewords = awgs.get('pre_word')
        if prewords and isinstance(prewords,str): prewords=[prewords]
        pre_n = len(prewords) if prewords else 0
        
        notwords = awgs.get('not_word')
        if notwords and isinstance(notwords,str): notwords=[notwords]
        not_n = len(notwords) if notwords else 0
        
        if isinstance(words,str): words=[words]
        word_n = len(words) 
        
        k, i = -1, 0
        if prewords:
            for line in fp:
                k += 1
                if len([ 1 for t in prewords if t in line])== pre_n:
                    i = k
            fp.seek(seek_size)    
        _i = 0
        _bsize = 0       
        for line in fp:
            _i += 1
            if _i>=i:
                if len([ 1 for t in words if t in line])== word_n:
                    if not_n and [ 1 for t in notwords if t in line]: continue
                    txts.append(line)
                    _bsize += len(line)
                    if len(txts)>100000:break 
                    if _bsize>bsize:break                    
    elif 'b' in mode :
        if  not encoding:
            from moofei._find import _get_chardet_detect as detect
            encoding = detect(fp.read(1024*100))[0]
            if encoding.upper()=='UTF-8-SIG': encoding='UTF-8'
            fp.seek(0)
        with fp:
            if seek_size: fp.seek(seek_size)
            txts = fp.read(bsize)
        if encoding: txts = txts.decode(encoding, 'ignore').split('\n')
        else: txts = [txts]
    else:            
        with fp:
            if seek_size: fp.seek(seek_size)
            for line in fp:
                n += len(line)
                txts.append(line)
                if n>=bsize: break
    tpage = st_size//bsize #totalpage
    if st_size%bsize: tpage+=1 
    params = dict(fname=fname, encoding=encoding, words=_words,
                                          st_size=st_size, 
                                          seek_size=seek_size, 
                                          bsize=bsize, 
                                          page=page, tpage=tpage,
                                          mode=mode)
                                          
    if awgs.get('tpl'):
        from moofei.util import jinja2_render
        if not isinstance(awgs['tpl'],str) or not os.path.isfile(awgs['tpl']):
            tpl = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates','view.html')
        else:
            tpl = awgs['tpl']
        params['curpage'] = params['page']+1
        params['path'] = fname
        params['txt'] = '\n'.join(txts)
            
        with open(tpl,'rb') as f:
            return jinja2_render(f, {'rs':params})    
    return txts, [st_size, encoding, params]
    
    
def main(cmd=None):
    import argparse
    parser = argparse.ArgumentParser(description="""Cat FileName <http://www.mufei.ltd>  """,
                                     epilog="QQqun: 226895834 ",
                                     formatter_class=argparse.RawDescriptionHelpFormatter
                                     )
    if cmd:
       parser.add_argument('cmd',  help="Command line mode; generally can be ignored") 
    parser.add_argument('name')
    parser.add_argument('-bsize','--bsize', type=int, default=100*1024)
    parser.add_argument('-page','--page', type=int, default=None)
    parser.add_argument('-mode','--mode', default='rb')
    parser.add_argument('-words','--words', nargs='*')
    parser.add_argument('-pre-word','--pre-word', nargs='*')
    parser.add_argument('-not-word','--not-word', nargs='*')
    
    parser.add_argument('-encoding','--encoding')
    parser.add_argument('-tpl','--tpl')
    parser.add_argument('--show-all', action='store_true')
    
    args = parser.parse_args()
    if '-h' in sys.argv :
        print(args)
    else:
        rs = _cat(args.name, 
                  bsize=args.bsize,
                  mode=args.mode,
                  page=args.page,
                  words=args.words,
                  pre_word=args.pre_word,
                  not_word=args.not_word,
                  encoding=args.encoding,
                  tpl=args.tpl,
                  show_all=args.show_all)
        if not args.tpl:          
            for line in rs[0]:
                print(line)  
            print('---------------end print',rs[1])            
        else:
            print(rs)
            
            
if __name__ == "__main__":         
    main()

