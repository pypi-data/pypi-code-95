#!/usr/bin/python
# coding: utf-8
# editor: mufei(ypdh@qq.com tel:15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

__all__ = ['Tree', ]

import sys, os
import traceback
from string import Template as string_Template
py = list(sys.version_info)
import copy
try:
    long
except NameError:
    long = int

import collections
def Dsort(d):
    '''
    >>> dd = [{"id":333, 'pid':0},
    ...      {"id":1, 'pid':0, 'g':2},
    ...      {"id":6, 'pid':0},
    ...      {"id":4, 'pid':0},
    ...      {"id":5, 'pid':0},
    ...      {"id":61, 'pid':6},
    ...      {"id":63, 'pid':6},
    ...      {"id":62, 'pid':6},
    ...      {"id":661, 'pid':61},
    ...      {"id":662, 'pid':61},
    ...      {"id":663, 'pid':62},
    ...      {"id":666, 'pid':63} ]
    >>> ddd = Tree(dd)
    >>> Dsort(ddd.list(name="list",pids=[1,6], hide=7))
    [OrderedDict([('g', 2), ('id', 1), ('list', []), ('pid', 0)]), OrderedDict([('id', 6), ('list', [OrderedDict([('id', 61), ('list', [OrderedDict([('id', 661), ('list', []), ('pid', 61)]), OrderedDict([('id', 662), ('list', []), ('pid', 61)])]), ('pid', 6)]), OrderedDict([('id', 62), ('list', [OrderedDict([('id', 663), ('list', []), ('pid', 62)])]), ('pid', 6)]), OrderedDict([('id', 63), ('list', [OrderedDict([('id', 666), ('list', []), ('pid', 63)])]), ('pid', 6)])]), ('pid', 0)])]
    >>> Tree(dd).getChildrens(6, name='list')
    [6, 61, 661, 662, 62, 663, 63, 666]
    >>> Dsort(Tree.deeps(dd))
    OrderedDict([(1, OrderedDict([('child', []), ('deep', 1), ('pid', [0])])), (4, OrderedDict([('child', []), ('deep', 1), ('pid', [0])])), (5, OrderedDict([('child', []), ('deep', 1), ('pid', [0])])), (6, OrderedDict([('child', [61, 63, 62]), ('deep', 1), ('pid', [0])])), (61, OrderedDict([('child', [661, 662]), ('deep', 2), ('pid', [6, 0])])), (62, OrderedDict([('child', [663]), ('deep', 2), ('pid', [6, 0])])), (63, OrderedDict([('child', [666]), ('deep', 2), ('pid', [6, 0])])), (333, OrderedDict([('child', []), ('deep', 1), ('pid', [0])])), (661, OrderedDict([('child', []), ('deep', 3), ('pid', [61, 6, 0])])), (662, OrderedDict([('child', []), ('deep', 3), ('pid', [61, 6, 0])])), (663, OrderedDict([('child', []), ('deep', 3), ('pid', [62, 6, 0])])), (666, OrderedDict([('child', []), ('deep', 3), ('pid', [63, 6, 0])]))])
    
    '''
    if isinstance(d,dict):
        _d = collections.OrderedDict()
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
            
    
class unStr(str):pass
class unList(list):pass 
    
class Tree:
    __tree = False
    
    def __init__(self, _d, pidCode='pid', childCode='id', sort='', is_copy=True):
        self.pidCode = pidCode
        self.childCode = childCode
        self.sort = sort or self.childCode
        
        if is_copy:
            _d = copy.deepcopy(_d)
            
        if isinstance(_d, dict):
            self._d = _d
        else:
            self._d = self.init_d(_d)
        self.__k = {}
            
    def init_d(self, lst):
        _d = self._d = {}
        c = self.childCode
        for d in lst:
            _d[d[c]] = d
        return _d

    def init_join(self, Ld, pidCode='pid', name='list'):
        _d = self._d
        for d in Ld:
            pid = d[pidCode]
            if pid in _d:
                _d[pid].setdefault(name, []).append(d)
    
    def getChildrens(self, pid=0, name="__tree", FL=None, deep=1000, pids=None):
        "获取子,孙子值 [id,int,int,int,id]: 深度搜索"
        #pids是真值必须是list 
        tree = self._d if self.__tree else self.tree(name)
        if FL is None and pids:
            L = pids
            FL = []
        else:
            if not FL :
                if FL is None: FL=[pid]
                else: FL.append(pid)
            else:
                if pid in FL: return FL
                FL.append(pid)                
            if deep==0: return FL
            L = tree[name] if (not pid or pid=='0') else tree[pid][name]
        for p in L:
            self.getChildrens(p, name, FL, deep-1)
        return FL
    
    def getChildrensDict(self, pid=0, name="__tree", FL=None, deep=1000, pids=None, valueCode=None):
        "获取子,孙子值 {id:{},int:{},int:{}}: 深度搜索"
        #pids是真值必须是list 
        tree = self._d if self.__tree else self.tree(name)
        if FL is None and pids:
            L = pids
            FL = {}
        else:
            if not FL :
                if FL is None: FL={}
            else:
                if pid in FL: return FL
            if valueCode:
                if pid in tree:
                    FL[pid] = tree[pid].get(valueCode,'')
                else:
                    print(pid, '(pid) Not In Tree!')
                    return FL    
            else:
                FL[pid] = tree[pid]
                FL[pid].pop(name, None)
                FL[pid].pop(self.childCode, None)    
                
            if deep==0: return FL
            L = tree[name] if (not pid or pid=='0') else tree[pid].get(name,[])
        for p in L:
            self.getChildrensDict(p, name, FL, deep-1, valueCode=valueCode)
        return FL
        
    @classmethod 
    def deeps(cls, List, pidCode='pid', childCode='id', name="deep", parent=0):
        "计算深度"
        _d = {}
        for d in List:
            _pid = d[pidCode]
            _id = d[childCode]
            _d[_id] = {'pid':[_pid],  'child':[]}

        _lost = [] #等级类别
        for d in List:
            _pid = d[pidCode]
            _id = d[childCode]
            if _pid==_id:
                _lost.append(_id)
                continue
            if _pid in _d:
                _d[_pid]['child'].append(_id)
            else:
                _lost.append(_id)

        if _lost :
            if len(_lost)>1:
                if parent in _lost: parent= min(_lost)-1
                for k in _lost: _d[k]['pid'][0] =  parent
            else:
                _parent = _lost[0]
        elif List:
            return {}
        else:
            #出现死循环
            return None
            
        p = _lost 
        deep = 0
        while p:
            deep += 1
            for k in  p:
                _d[k][name] = deep
            p = [k for k in _d if _d[k]['pid'][0] in p]
            for k in p:
                pid = _d[k]["pid"]
                _d[k]["pid"] = pid+_d[pid[0]]["pid"]
        return _d
    
    def tree(self, name='__tree'):
        #[{},{}]转化为{k:{'list':[int]}} ~~~~ list:不深层
        _d = self._d
        __tree = _d.setdefault(name, [])
        pid = self.pidCode

        #list插入
        for k in _d.keys():
            if k==name: continue
            d = _d[k]
            p = d.get(pid)
            d.setdefault(name, [])
            if not p or p=='0':
                __tree.append(k)
            elif p in _d:
                pd = _d[p]
                pd.setdefault(name, []).append(k)
                
        sort = self.sort
        #排序
        for k in _d.keys():
            if k==name:
                _d[k] = sorted(_d[k], key=lambda x: _d[x][sort])
            else:
                _d[k][name] = sorted(_d[k][name], key=lambda x: _d[x][sort] or 0)
                
        self.__tree = True
        return _d
            
    def list(self, name='__tree', pid=0, deep=0, pids=None, hide=None):
        #"[{list:}, {}]; ~~~~ list: 递归深层"
        #'相当于tree的递归深层'
        if deep<0:
            pid_d = self._d.get(pid)
            if pid_d: return self.list(name, pid_d[self.pidCode], deep+1)
           
        tree = self._d if self.__tree else self.tree(name)
        
        if pids is None:
            try:
                __tree = tree[name] if (not pid or pid=='0' or pid not in tree) else tree[pid][name]
            except KeyError:
                raise
        else:
            __tree = pids
        
        if hide and hide!='0':
            if isinstance(hide,(str, int, long)):
                hide = [hide]
            for h in hide:
                if h in __tree: __tree.remove(h)
        
        for x in range(len(__tree)):
            _id = __tree[x]
            if isinstance(_id, dict):
                continue
            if _id in self.__k: continue
            #if _id == name: continue
            if _id in tree: 
                self.__k[_id] = 1
                __tree[x] = tree[_id]
                __tree[x][name] = self.list(name, _id)
                
        return __tree 
    
    @classmethod
    def to_dot(cls, List, id_key='id', pid_key='pid', val_key='name', sort_key='', deep=0, pid=0, dot='- ',reverse=False, find=None, tpl=None, Ls=None):
        '''
        >>> List =[{'id':1,'pid':0, 'name':1, 'nid':1},
        ...   {'id':2,'pid':0, 'name':1, 'nid':2},
        ...   {'id':11,'pid':1, 'name':1, 'nid':2},
        ...   {'id':21,'pid':2, 'name':1, 'nid':2},
        ...   {'id':111,'pid':11, 'name':111, 'nid':2},
        ...   {'id':112,'pid':11, 'name':112, 'nid':1}
        ...   ]
        >>> Tree.to_dot(List, sort_key='nid', tpl='$id$dots$name') #tpl='<option value="$id">$dots$name</option>'
        '1111- 1112- - 112111- - 1112121- 1'
        '''  
        L = [d for d in List if d[pid_key]==pid]        
        if sort_key:
            L=sorted(L, key=lambda e: e[sort_key] or 0, reverse=reverse) 
        if Ls is None: Ls = []
        if tpl:
            for d in L:
                if tpl is True:
                    s = '<option value="%s">%s%s</option>'%(d[id_key],dot*deep, d[val_key])
                else:
                    s = string_Template(tpl).substitute(dots=dot*deep, **d)
                fS = cls.to_dot(List, id_key, pid_key, val_key, sort_key, deep+1, d[id_key], dot, reverse, find, tpl=tpl) 
                if find and isinstance(fS, unStr) and not fS and not find(d): 
                    continue
                else:
                    s +=  fS
                    Ls.append(s)
            rs = ''.join(Ls)
            if find and not rs: rs = unStr()
        else:
            for d in L:
                if isinstance(d,dict):
                    d['deep'] = deep
                elif isinstance(d,tuple):
                    d = list(d)
                if dot: d[val_key] = "%s%s"%(dot*deep,d[val_key])
                fL = cls.to_dot(List, id_key, pid_key, val_key, sort_key, deep+1, d[id_key], dot, reverse, find)
                if find and isinstance(fL, unList) and not fL and not find(d):
                    continue    
                else:
                    Ls.append(d)
                    Ls += fL    
            rs = Ls
            if find and not rs: rs = unList()
        return rs
    
        
if __name__ == "__main__":  
    import doctest
    doctest.testmod() #verbose=True        


