# coding:utf-8
'''
第三方库
作者：PYmili
时间：2021/8/12

'''
import datetime
import time
import random
import pytz
import timezones
from dateutil import tz
import re
import time

def OStime(time_a):
    if time_a == 'nyr':
        time_nyr = time.strftime("%Y/%m/%d")
        print(time_nyr)
    if time_a == '12xs':
        time_12xs = time.strftime("%I:%M:%S")
        print(time_12xs)
    if time_a == '24xs':
        time_24xs = time.strftime("%H:%M:%S")
        print(time_24xs)
    if time_a == 'jh':
        time_jh = time.strftime("%Y/%m/%d %H:%M:%S")
        print(time_jh)
    if time_a == 'm':
        m = (datetime.datetime.now().second)
        print(m)
    if time_a == 'f':
        f = (datetime.datetime.now().minute)
        print(f)
    if time_a == 's':
        s = (datetime.datetime.now().hour)
        print(s)
    if time_a == 'r':
        rq = (datetime.datetime.now().day)
        print(rq)
    if time_a == 'y':
        yf = (datetime.datetime.now().month)
        print(yf)
    if time_a == 'n':
        nf = (datetime.datetime.now().year)
        print(nf)
    if time_a == 'GMT-8-Time_MS':
        gmt  = time.gmtime()
        millis = gmt.tm_hour*3600000 + gmt.tm_min*60000 + gmt.tm_sec*1000
        print(millis)
    if time_a == 'Running_time':
        s_time = time.time()
        sqrt_list = [x**2 for x in range(1, 1000000, 3)]
        e_time = time.time()
        print("{:.5}".format(e_time-s_time))
    if time_a == 'stamp':
        stamp = (time.time())
        print(stamp)
    if time_a == 'ctime':
        ctime = (time.ctime())
        print(ctime)
