# -*- coding: utf-8 -*-
import re
import time
import random
import string
import pymysql
import hashlib
import sqlite3
import requests
from datetime import datetime

class mysqldb():
    def __init__(self,host='',port=3306,db='',user='',passwd='',charset='utf8'):
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd,charset=charset,read_timeout=10,write_timeout=10)
        self.cur = self.conn.cursor(cursor = pymysql.cursors.DictCursor)

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

class sqlite(object):
    def __init__(self,sqlcmd,db_name):
        self.sqlcmd = sqlcmd
        self.db_name = db_name

    def run(self):
        return self.sqlcommit()

    def sqlcommit(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            sqlex=cursor.execute(self.sqlcmd)
            sqlrc=cursor.rowcount
            sqlfa=cursor.fetchmany(200)
            cursor.close()
            conn.commit()
            conn.close()
            if self.sqlcmd.split(" ")[0]=='select':
                return sqlfa
            else:
                return sqlrc
        except Exception as error:
            return "sqlite数据库执行发生错误:"+str(error)

def  mysqlex(sqlcmd,host='',port=3306,db='',user='',passwd='',charset='utf8',args=[]):
    if host =='':
        with mysqldb() as db:
            try:
                if args!=[]:
                    db.executemany(sqlcmd,args)
                else:
                    db.execute(sqlcmd)
                if sqlcmd.split(" ")[0]=="select":
                    return db.fetchall()
                else:
                    return db.rowcount
            except Exception as error:
                return "mysql数据库执行发生错误:"+str(error)
    else:
        with mysqldb(host,port,db,user,passwd,charset) as db:
            try:
                if args!=[]:
                    db.executemany(sqlcmd,args)
                else:
                    db.execute(sqlcmd)
                if sqlcmd.split(" ")[0]=="select":
                    return db.fetchall()
                else:
                    return db.rowcount
            except Exception as error:
                return "mysql数据库执行发生错误:"+str(error)

class date_time(object):
    def __init__(self):
        self.year=datetime.now().year
        self.month=datetime.now().month
        self.day=datetime.now().day
        self.hour=datetime.now().hour
        self.minute=datetime.now().minute
        self.second=datetime.now().second
        self.now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.time=datetime.now()

def send_msg(title='',content='',msg_url=None,touser="@all"):
    url='http://msg.msgbox.xyz/send_msg'
    data={"title":title,"content":content,'url':msg_url,"touser":touser}
    r=requests.post(url,json=data,timeout=5)
    return r.text

def ding_msg(title='',content='',msg_url=None):
    url='http://msg.msgbox.xyz/ding_msg'
    data={"title":title,"content":content,'url':msg_url}
    r=requests.post(url,json=data,timeout=5)
    return r.text

def mprint(*string):
    printstr=""
    if len(string)!= 0:
        for s in string:
            if printstr=="":
                printstr=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" "+str(s)
            else:
                printstr=printstr+" "+str(s)
    print(printstr)

def format_cookie(MyCok):
    return eval('{"'+MyCok.replace('=','":"').replace(';','","').replace('":"":"','==').replace(" ","")+'"}')

def write_str(Str,File="./temp.log"):
    with open(File, 'a') as File:
        File.write(Str+"\n")
        print ("写入完成！")

def random_agent(UserAgentList):
    return UserAgentList[int(random.random()*len(UserAgentList))]

def timestamp(type=0):
    thistime=time.time()
    if type==0:
        return int(thistime)
    else:
        return int(round(thistime * 1000))

def md5_hex(text):
    return hashlib.md5(text.encode()).hexdigest()

def hex_to_rgb(hex):
    r = int(hex[1:3],16)
    g = int(hex[3:5],16)
    b = int(hex[5:7], 16)
    rgb = str(r)+','+str(g)+','+str(b)
    return rgb

def rgb_to_hex(rgb):
    RGB = rgb.split(',')
    color = '#'
    for i in RGB:
        num = int(i)
        color += str(hex(num))[-2:].replace('x', '0').upper()
    return color

def gen_uid():
    return md5_hex(str(''.join(random.sample(string.ascii_letters + string.digits,18)))+str(timestamp(1)))

def link_str(str1,str2,lstr):
    if str(str1) == "":
        return str(str2)
    else:
        return str(str1)+str(lstr)+str(str2)

def find_string(Str,Key):
    return re.compile(Key).findall(str(Str))

def get_url(string):
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    url = re.findall(pattern,string)
    return url
