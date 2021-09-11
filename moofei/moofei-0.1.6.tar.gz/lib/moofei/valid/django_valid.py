#!/usr/bin/python
# -*- coding: UTF-8 -*-
# editor: moofei
'''
by 牧飞 _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''
__all__ = ['valid', 
           ]

import re
#import sys; sys.path.append('..') #
try:
    from .. import _valid
    from .._valid import  ValidDict, ValidMethod,  ValidResultParse, unVal
except (ImportError,ValueError):
    from moofei import _valid
    from moofei._valid import  ValidDict, ValidMethod,  ValidResultParse, unVal
import time
import json
import traceback
try:
    from inspect import signature
    #list(inspect.signature(s).parameters)
except:
    signature = None


class VALID(_valid.VALID):
    @classmethod
    def set_error_value(cls, state, value, method):
        d = {'date':'日期不正确',
             'time':'时间不正确',
             'ip':"IP地址不正确",
             'lanip':"局域网内部IP不正确",
              'url':"网址不正确", 
              'money':"金额不正确",
              'password':'密码强度太轻',
              'password0':'密码强度太轻',
              'password1':'密码强度太轻',
              'mail':'邮箱格式不正确',
              'email':'邮箱格式不正确',
              'phone':'电话格式不正确',
              'datetime':"日期时间不正确",
              'domain':"域名格式不正确", 
              'idcard':"证件号码有误",
              "host":"域名格式不正确", 
              "sex":"性别输入错误",
              }
        if method in d:
            return {'error':{
                        'message': d[method]
                        }
                     }
        return value
        
    @classmethod
    def error(cls, func_name, regula, value, result=None, key=None, code=-32602):
        if isinstance(result, dict) and result.get('error'): 
            if key and 'key' not in result: result['key'] = key
        else:
            if result and not regula and not value:
                message = result
            elif 0 and func_name:
                message = "Invalid params. Checked (valid) '%s' in the '%s' function, so the value should not be '%s'"%(regula, func_name, value or 'null')
            else:
                message = "Invalid params. Checked (valid) '%s' should  not be '%s'"%(regula, value or 'null')
            result = {'error':{
                        'code':code,
                        'regula':regula,
                        'message': message
                        }
                     }
            if key and 'key' not in result: result['key'] = key
        return result     
    
    
def dict_django_update(d, *args):
    for arg in args:
        if not arg: continue
        for k in arg:
            d[k] = v = (getattr(arg, 'getlist', None)  or arg.get)(k) #arg.getlist(k)
            if isinstance(v, (list,tuple)) :
                if len(v)==1:
                    d[k] = v[0]
                elif len(v)==2 and v[0]==v[1]:
                    d[k] = v[0]
    return d        
        
    
class valid:
    Debug = False
    __valid_pre_check = {}
    
    @classmethod
    def setPreCheck(cls, param, callback=None):
        def wrap(callback):
            cls.__valid_pre_check[param] = callback
        if callback:
            cls.__valid_pre_check[param] = callback
            return
        return wrap
    
    @classmethod
    def add(cls, name, is_cover=False):
        """valid.add
           >>> @valid.add('beter')
           ... def better(s): return 1,s
           >>> valid.dict(['a:beter'], dict(a="ddddddddddd")) 
        """
        def wrap(fn):
            VALID.addCheck(fn, name=name, is_cover=is_cover)
            return fn
        return wrap
        
    @classmethod
    def addCheck(cls, fn, name=None, is_cover=False):
        """valid.addCheck
           >>> def better(s): return 1,s
           >>> valid.addCheck(better, 'beter') and None
           >>> valid.dict(['a:beter'], dict(a="ddddddddddd")) 
        """
        VALID.addCheck(fn, name=name, is_cover=is_cover)
        return cls
    
    @staticmethod
    def dict(validArgs, awgs):
        '''valid.dict
        >>> valid.dict(['a:int', 'b:true', 'c:ip', r'f:^\d+$'], dict(a=44, b='sss', c='127.0.0.1', f='9ddd9'))
        ('f', '^\\\\d+$')
        '''
        return ValidDict(validArgs, awgs, validCls=VALID)
    
    @staticmethod
    def kDict(validArg, *args, **awgs):
        """valid.kDict
        >>> var_keys = ["var_title", "var_code", "var_memo", "var_content", "upd_can:int", "nid:int"]
        >>> valid.kDict(var_keys, {"upd_can":"0"})
        {'upd_can': 0}
        """
        rs = ValidResultParse(validArg, args, validCls=VALID, **awgs)
        return rs
        
    @staticmethod
    def kDictReal(validArg, *args, **awgs):
        """
           isNotTrue=0, isStrict=0, pops=[]
           >>> var_keys = ["var_title", "var_code", "var_memo", "var_content", "upd_can:int;true", "nid:int"]
           >>> valid.kDictReal(var_keys, {"upd_can":"0"})
           {'upd_can': 0}
        """
        rs = ValidResultParse(validArg, args, validCls=VALID, isNotTrue=1, **awgs)
        return rs

    
    @staticmethod
    def func(validArgs=None, permit='', rate=None, block=False):
        '''valid.func
        >>> @valid.func(['a:int', 'b:true', 'c:ip', r'f:^\d+$'])
        ... def A(a,b,c,d=3,e=5, f='', **m): pass
        >>> A('3', 'ee', '1.1.1.1',f='64')
        >>> A.validArgs
        ['a:int', 'b:true', 'c:ip', 'f:^\\\\d+$']
        '''
        return ValidMethod(validArgs, validCls=VALID, permit=permit, rate=rate, block=block)

    
    
    @staticmethod
    def doc(cls, allow_api):
        #header("Content-type: text/html;charset=utf-8");
        rs = []
        for api in allow_api:
            fn = getattr(cls, api)
            docs = (fn.func_doc or '').replace('\n', '\n<br>').split('\n', 1)
            doc = docs[1].strip() if len(docs)>1 else None
            validArgs =  getattr(fn, "validArgs", None) or []
            d = {'valid':validArgs,  'doc':doc, 'name':docs[0].strip(), 'api':api}
            rs.append(d)
        return rs
    
    @classmethod
    def request(cls, fn,  rq, **awgs):
        '''request
        >>> @valid.func(['token:', 'request:','a:int', 'c:code'])
        ... def index_func(token, request, a, c="", **awgs):
        ...     print(token, request, a, c)
        ...     return {'result':{'token':token, 'a':a, 'c':c, 'awgs':awgs}}    
        >>> def index(request):
        ...     return JsonResponse(valid.request(index_func, request))
        '''
        t0 = time.time()
        
        _fc = cls.__valid_pre_check
        
        attrs =  getattr(fn, "validArgs", None) or [] #attrs=fn.validArgs
        if attrs:
            dft,keys,argext = fn.func_dft
            isAwgs = argext[1]
                
        args = []
        keysL = []
        #d = rq.values
        if rq.content_type and 'application/json' in rq.content_type:
            chunk = rq.read()
            form = json.loads(chunk) if chunk else {}
        else:
            form = rq.POST
        d = dict_django_update({}, rq.GET, form, rq.FILES)
        
        for attr in attrs:
            param = attr.split(':')[0]
            keysL.append(param)
            if param in awgs: 
                #pass #val = awgs.pop(param)
                if param in keys:
                    val = awgs.pop(param)
                    args.append(val)  
            else: 
                #val = d.get(param, '') #val = rq.form.get(param, '')
                if param in d:
                    val = d[param]
                else:
                    val = unVal()
                
                if param=='token' and val in ("", None, "null", "undefined"):
                    val = rq.META.get('HTTP_X_TOKEN') or rq.COOKIES.get(param, '')
                if param == 'request' and val=="":
                    val = rq
                elif param == 'remote_addr':
                    val = rq.META['REMOTE_ADDR']
                if param in keys:
                    args.append(val) #if val=='': val=None
                elif isAwgs:
                    awgs[param] = val
            #if param=='token' and val in staticTokenCache:
            #    rq.environ['HTTP_X_USER_ID'] = staticTokenCache[val]['user_id']
            if param in _fc:
                rs = _fc[param](val, fn, rq)
                if rs: return rs
                
        if attrs and isAwgs:
            for attr in d:
                if attr not in keysL:
                    awgs[attr] = d[attr]
                    if attr in _fc:
                        rs = _fc[attr](d[attr], fn, rq)
                        if rs: return rs

        try:
            rs = fn(*args, **awgs)
        except TypeError:
            strd = str(d)
            #if len(strd)<10000: print(strd)
            #saveErrCaller()
            print(traceback.format_exc())
            if valid.Debug and time.time()-t0>0.5: print('valid.request',fn, time.time()-t0)
            raise
        if valid.Debug and time.time()-t0>0.5: print('valid.request',fn, time.time()-t0)            
        return  rs



        
if __name__ == "__main__":
    import doctest
    doctest.testmod() #verbose=True
    























    