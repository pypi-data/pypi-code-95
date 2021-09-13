#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   update.py
@Time    :   2021/05/08
@Author  :   levonwoo
@Version :   0.1
@Contact :   
@License :   (C)Copyright 2020-2021
@Desc    :   日线数据测试模块
'''

# here put the import lib
import datetime
import time

from QuadQuanta.config import config
from QuadQuanta.data.save_data import save_bars

if __name__ == '__main__':
    # while True:
    today = datetime.date.today()
    hour = datetime.datetime.now().hour
    start_time = config.start_date + ' 09:00:00'
    end_time = str(today) + ' 17:00:00'
    save_bars(start_time, end_time, frequency='daily', database='jqdata')
    # try:
    #     if hour < 17 and hour >= 6:
    #         save_all_jqdata('2014-01-01',
    #                         '2014-07-01',
    #                         frequency='minute',
    #                         database='jqdata')
    # except Exception as e:
    #     print(e)
    #     break
    # time.sleep(60)