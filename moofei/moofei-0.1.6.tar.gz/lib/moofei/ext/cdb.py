#!/usr/bin/python
# coding: utf-8
# editor: mufei(ypdh@qq.com tel:15712150708)
'''
牧飞 _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

__all__ = ['DB']

from moofei._db import _db
import os,sys,json
import re,time
import datetime
import decimal
from moofei._find import _get_chardet_detect as detect
_py = list(sys.version_info)
try:
    from pymysql import escape_string
except:
    from pymysql.converters import escape_string
            
try:
    unicode
except:
    unicode = str

def DBdefault(obj):  
    '''
    if isinstance(obj, MyClass):  
        return {'a':obj.a,'b':obj.b}  
    '''
    if isinstance(obj,  datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')  
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, datetime.timedelta):
        return str(obj)
    elif isinstance(obj, bytes):
        #print(obj)
        encoding = detect(obj)[0]
        return obj.decode(encoding, 'ignore')  
    else:
        print(type(obj))
        obj = str(obj)
        raise TypeError('%r is not JSON serializable' % obj)
DBdefault.enableTypes = ['datetime.datetime','datetime.date','decimal.Decimal','datetime.timedelta']


class DB(_db):
    @classmethod
    def dumps(cls, obj, *args, **awgs):
        " Serialize ``obj`` to a JSON formatted ``str``."
        awgs.setdefault('default', DBdefault)
        return json.dumps(obj, *args,**awgs)
        
    def extractTableSql(self, table, columns=None, scheme='mysql'):
        columns = columns or self.columns 
        sqls = ["CREATE TABLE if not exists %s("%table]
        for k in columns:
            if k[0]==table:
                v =  columns[k]
                if _py[0]==2: v = [ str(e) if isinstance(e,unicode) else e  for e in v]
                #print(v)
                sql=self.add_field(table, 
                    k[1], 
                    field_type=v[2],  
                    required= v[1]=='NO', 
                    default=v[0], 
                    comment=v[4],  
                    unique=v[3] in ('UQ','UNI'), 
                    primary=v[3] in ('PK','PRI'), 
                    to_sql='short', 
                    scheme=scheme,
                    debug=0)
                if len(sqls)>1:
                    sqls.append('\t,'+k[1]+' '+sql)
                else:
                    sqls.append('\t'+k[1]+' '+sql)
        sqls.append(')')
        sql = '\n'.join(sqls)
        return sql
        
    def extractInsertSql(self, table, data):
        table = str(table)
        _keys,_args = [], []
        for k, v in data.items():
            _keys.append(k)
            _args.append(v)
            
        _keys = ','.join(str(v) for v in _keys)
        _vals = []
        for v in  _args:
            if v is None: v='null'
            elif isinstance(v,str) or isinstance(v,datetime.datetime) or isinstance(v,unicode):
                if _py[0]==2 and isinstance(v,unicode):
                    v = v.encode('utf-8')
                v = '"%s"'%escape_string(str(v))
            else:
                v = str(v)
            _vals.append(v)    
        _vals =  ','.join(_vals)       
        #_vals = ','.join( '\'' +str(v) +'\'' if isinstance(v,str) or isinstance(v,datetime.datetime) or isinstance(v,unicode) else str(v) for v in _args)
        sql="INSERT INTO %s(%s) VALUES (%s)"%(table, _keys, _vals)
        return sql
        
    def extractAll(self, out_dir, cache=True, is_cover=False, tables=None, use_db=None):
        def callback(data, fp):
            i = 0
            for d in data:
                fp.write(self.dumps(d)+'\n')
                with open(cachefile,'w') as f :
                   f.write(json.dumps(cacheDict))                
                if i and i%10000==0: print(i)
                i += 1
                
        if not os.path.isdir(out_dir):
            print(out_dir, 'Not Dir.....')
            return
        if use_db is True: use_db = self.DEFAULT_DATABASE   
        cacheDict = {} 
        cachefile = None         
        if cache:
            cachefile = os.path.join(out_dir, '.cache.json')
            if not os.path.isfile(cachefile) or is_cover:
                with open(cachefile,'w') as fp: fp.write('{}')
                cacheDict = {}
            else:
                cacheDict = json.loads(open(cachefile,'r').read())
                
        if tables:
            if isinstance(tables, str): tables=[tables]
        else:
            tables = self.tables
        tables.sort()
        columns = self.columns
        dPK = {}
        for table in tables:
            print(table)
            _fields = {}
            pkname = None
            pktype = None
            cacheTable = cacheDict.setdefault(table, {})
            for k,v in columns.items():
                if k[0]!=table:continue
                if v[3] in ('PK','PRI'):
                    pkname = dPK[table]=k[1]
                    pktype = v[2]
                _fields[k[1]] = v[2]
                
            if table not in dPK: 
                for k,v in columns.items():
                    if k[0]!=table:continue
                    if v[3] in ('UQ','UNI'):
                        pkname = dPK[table]=k[1]
                        pktype = v[2]
                        if re.search('int',pktype): break
                    
            out_file = os.path.join(out_dir, '%s.sql'%table)
            if is_cover or not cache:
                fp = open(out_file, 'wb')
            else:
                if cache and os.path.isfile(out_file):
                    st_size = os.stat(out_file).st_size
                    if st_size:
                        fp = open(out_file, 'rb')
                        if fp.read(17)==b'-- -- start -- --':
                            cacheTable['initSQL'] = 1
                        fp.seek(0)
                        if st_size>100:
                            fp.seek(st_size-100)                         
                        if fp.read().split(b'\n')[-1][:15] == b'-- -- end -- --':
                            cacheTable['endSQL'] = 1
                            continue
                if table not in dPK:
                    fp = open(out_file, 'wb')
                    cacheTable.clear()
                else:    
                    fp = open(out_file, 'ab+') 
            if not cacheTable.get('initSQL'):
                startmemo = '-- -- start -- --'+time.ctime()+'----\n'
                fp.write(startmemo.encode('utf-8'))
                
                if use_db:
                    fp.write(b'use '+use_db.encode('utf-8')+b'          ;\n')
                    
                sql = self.extractTableSql(table, columns)
                try:
                    fp.write(sql.encode('utf-8'))
                except:
                    if _py[0]==2: fp.write(sql)                    
                #fp.write(sql.encode('utf-8'))
                fp.write(b';\n')
                if cache:
                    cacheTable['initSQL'] = 1
                    with open(cachefile,'w') as f :
                        f.write(json.dumps(cacheDict))
                print(table, 'initSQL', 'saved...')

            count = self.count(table)    
            initROW = cacheTable.setdefault('initROW',0)
            if re.search('char',pktype):
                initPK = cacheTable.setdefault('initPK','')
            else:
                initPK = cacheTable.setdefault('initPK',-count)
            
            if isinstance(count, (str,tuple,list,dict)):
                print(count)
                continue
            #print(count)    
            if count > initROW:
                if table in dPK:
                    pk = initPK
                    n = initROW
                    while n<count:
                        _data = self.query(table, page_size=10000, where={dPK[table]+'__gt':pk}, orderby=dPK[table])
                        if _data.get('error'): 
                            raise
                        data = _data['result']
                        if not data: break
                        
                        pk = max([d[dPK[table]] for d in data])
                        for d in data:
                            sql = self.extractInsertSql(table, d)
                            try:
                                fp.write(sql.encode('utf-8'))
                            except:
                                if _py[0]==2:
                                    fp.write(sql)
                                else:
                                    print(sql, d)
                                    raise
                            fp.write(b';\n')
                            n += 1
                            if cache:
                                cacheTable['initPK']  = d[dPK[table]]
                                cacheTable['initROW'] = n
                                try:
                                    with open(cachefile,'w') as f :
                                        f.write(json.dumps(cacheDict)) 
                                except KeyboardInterrupt:
                                    with open(cachefile,'w') as f :
                                        f.write(json.dumps(cacheDict))
                                    raise    
                            if n and n%10000==0: print(table, 'initROW', n, cacheTable['initPK'], count)
                else:
                    raise
                    
                '''        
                elif count>10000 and table not in dPK:
                    data = self.query(table, page_size=10000)['result']
                    callback(data)      
                else:
                    data = self.select(table)['result']
                    callback(data)
                '''
                
                endtmemo = '-- -- end -- --'+time.ctime()+'----\n'
                fp.write(endtmemo.encode('utf-8'))
                cacheTable['endSQL'] = 1
                with open(cachefile,'w') as f :
                    f.write(json.dumps(cacheDict))    
            fp.close()        
          
            
        
    def extract_test(self, out_file, limit_nums=30000, empty_out=False, tables=None):
        def callback(data):
            i = 0
            for d in data:
                #print(d)
                fp.write(self.dumps(d)+'\n') 
                if i and i%10000==0: print(i)
                i += 1
                
        fp = open(out_file,'w')
        if tables:
            if isinstance(tables, str): tables=[tables]
        else:
            tables = self.tables
        tables.sort()
        columns = self.columns
        dPK = {}
        for table in tables:
            for k,v in columns.items():
                if k[0]!=table:continue
                if v[3] in ('PK','PRI'):
                    dPK[k[0]]=k[1]
                fp.write(str(k)+':'+str(v)+'\n')
        fp.write('\n')
        
        for table in tables:
            count = self.count(table)
            if isinstance(count, (str,tuple,list,dict)):
                print(count)
                continue
            if not empty_out and not count: continue
            if count>limit_nums: continue
            fp.write('\n')
            fp.write('-'*10+table+'-'*10+'\n')
            print('start save....',table, count, dPK.get(table,''))
            data=[]
            if count>10000 and table in dPK:
                pk = 0
                n = 0
                while n<count: 
                    #sql = "select top 10000 * from %s where %s>%s order by %s"%(table, dPK[table],pk, dPK[table])
                    #data = self.fetchallDict(sql)['result']
                    data = self.query(table, page_size=10000, where={dPK[table]+'__gt':pk}, orderby=dPK[table])['result']
                    if not data: break
                    pk = max([d[dPK[table]] for d in data])
                    callback(data)
                    print('pk=', pk)
            elif count>10000 and table not in dPK:
                data = self.query(table, page_size=10000)['result']
                callback(data)      
            else:
                data = self.select(table)['result']
                callback(data)
            
        fp.close()
            