#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/6/20 下午12:14
@File    : datetime.py
@contact : mmmaaaggg@163.com
@desc    : 
"""

import logging
import re
from datetime import datetime, date, timedelta

import numpy as np
import pandas as pd
import pytz

logger = logging.getLogger(__name__)

STR_FORMAT_DATE = '%Y-%m-%d'
STR_FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
STR_FORMAT_DATETIME2 = '%Y-%m-%d %H:%M:%S.%f'
STR_FORMAT_TIME = '%H:%M:%S'
PATTERN_DATE_FORMAT_RESTRICT = re.compile(r"\d{4}(\D)*\d{2}(\D)*\d{2}")
PATTERN_DATE_FORMAT = re.compile(r"\d{4}(\D)+\d{1,2}(\D)+\d{1,2}")
PATTERN_DATETIME_F_FORMAT_RESTRICT = re.compile(r"\d{4}(\D)*\d{2}(\D)*\d{2} \d{2}(\D)*\d{2}(\D)*\d{2}(\D)+\d{3,6}")
PATTERN_DATETIME_F_FORMAT = re.compile(r"\d{4}(\D)+\d{1,2}(\D)+\d{1,2} \d{1,2}(\D)+\d{1,2}(\D)+\d{1,2}(\D)+\d{1,6}")
PATTERN_DATETIME_FORMAT_RESTRICT = re.compile(r"\d{4}(\D)*\d{2}(\D)*\d{2} \d{2}(\D)*\d{2}(\D)*\d{2}")
PATTERN_DATETIME_FORMAT = re.compile(r"\d{4}(\D)*\d{1,2}(\D)*\d{1,2} \d{1,2}(\D)*\d{1,2}(\D)*\d{1,2}")


def date_2_str(dt, format_str=STR_FORMAT_DATE):
    """将日期类型转换为字符串"""
    if dt is not None and type(dt) in (date, datetime, pd.Timestamp):
        dt_str = dt.strftime(format_str)
    else:
        dt_str = dt
    return dt_str


def datetime_2_str(dt, format_str=STR_FORMAT_DATETIME):
    if dt is not None and type(dt) in (date, datetime, pd.Timestamp):
        dt_str = dt.strftime(format_str)
        # print(type(dt), '->', dt_str)
    elif isinstance(dt, pd.DatetimeIndex):
        dt_str = [x.strftime(format_str) for x in dt]
        # print(type(dt), '-->', dt_str)
    else:
        dt_str = dt
        # print(type(dt), '没有转换', dt)
    return dt_str


def time_2_str(t):
    if t is not None and isinstance(t, timedelta):
        seconds = t.seconds
        hours, minutes = divmod(seconds, 3600)
        minutes, secs = divmod(minutes, 60)
        dt_str = "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, secs)
        # print(type(t), '->', dt_str)
    else:
        dt_str = str(t)
        # print(type(t), '没有转换', t)
    return dt_str


def date_time_2_str(d, t):
    """将日期与时间组合成  '%Y-%m-%d %H:%M:%S' 字符串 """
    return date_2_str(d) + ' ' + time_2_str(t)


def str_2_datetime(datetime_str, format_str=STR_FORMAT_DATETIME):
    if datetime_str is not None:
        if type(datetime_str) == str:
            date_ret = datetime.strptime(datetime_str, format_str)
        elif type(datetime_str) in (pd.Timestamp, datetime):
            date_ret = datetime_str
        else:
            date_ret = datetime_str
    else:
        date_ret = datetime_str
    return date_ret


def str_2_bytes(input_str):
    """
    用于将 str 类型转换为 bytes 类型
    :param input_str:
    :return:
    """
    return input_str.encode(encoding='GBK')


def bytes_2_str(bytes_str):
    """
    用于将bytes 类型转换为 str 类型
    :param bytes_str:
    :return:
    """
    return str(bytes_str, encoding='GBK')


def timedelta_2_str(td):
    """
    用于将 pd.Timedelta 类型转换为 str 类型
    :param td:
    :return:
    """
    if isinstance(td, pd.Timedelta):
        ret = str(td).split()[-1]
    else:
        ret = td
    return ret


def pattern_data_format(data_str):
    """
    识别日期格式（例如：2017-12-23），并将其翻译成 %Y-%m-%d 类似的格式
    :param data_str:
    :return:
    """
    date_str_format = PATTERN_DATE_FORMAT_RESTRICT.sub(r'%Y\1%m\2%d', data_str)
    if date_str_format == data_str:
        date_str_format = PATTERN_DATE_FORMAT.sub(r'%Y\1%m\2%d', data_str)
    return date_str_format


def pattern_datatime_format(data_str):
    """
    识别日期格式（例如：2017-12-23 12:31:56），并将其翻译成 %Y-%m-%d %H:%M:%S 类似的格式
    识别日期格式（例如：2017-12-23 12:31:56.123），并将其翻译成 %Y-%m-%d %H:%M:%S.%f 类似的格式
    :param data_str:
    :return:
    """
    # 带 %f
    date_str_format = PATTERN_DATETIME_F_FORMAT_RESTRICT.sub(r'%Y\1%m\2%d %H\3%M\4%S\5%f', data_str)
    if date_str_format != data_str:
        return date_str_format

    date_str_format = PATTERN_DATETIME_F_FORMAT.sub(r'%Y\1%m\2%d %H\3%M\4%S\5%f', data_str)
    if date_str_format != data_str:
        return date_str_format

    # 不带 %f
    date_str_format = PATTERN_DATETIME_FORMAT_RESTRICT.sub(r'%Y\1%m\2%d %H\3%M\4%S', data_str)
    if date_str_format != data_str:
        return date_str_format
    date_str_format = PATTERN_DATETIME_FORMAT.sub(r'%Y\1%m\2%d %H\3%M\4%S', data_str)
    if date_str_format != data_str:
        return date_str_format

    return date_str_format


def try_2_date(something):
    """
    兼容各种格式尝试将 未知对象转换为 date 类型，相对比 str_2_date 消耗资源，支持更多的类型检查，字符串格式匹配
    :param something:
    :return:
    """
    if something is None:
        date_ret = something
    else:
        something_type = type(something)
        if something_type in (int, np.int64, np.int32, np.int16, np.int8):
            something = str(something)
            # something_type = type(something)
        if type(something) == str:
            date_str_format = pattern_data_format(something)
            date_ret = datetime.strptime(something, date_str_format).date()
        elif type(something) in (pd.Timestamp, datetime):
            date_ret = something.date()
        else:
            date_ret = something
    return date_ret


def try_2_datetime(something):
    """
    兼容各种格式尝试将 未知对象转换为 date 类型，相对比 str_2_date 消耗资源，支持更多的类型检查，字符串格式匹配
    :param something:
    :return:
    """
    if something is None:
        date_ret = something
    else:
        something_type = type(something)
        if something_type in (int, np.int64, np.int32, np.int16, np.int8):
            something = str(something)
            # something_type = type(something)
        if type(something) == str:
            date_str_format = pattern_datatime_format(something)
            date_ret = datetime.strptime(something, date_str_format).date()
        elif isinstance(something, datetime):
            date_ret = something
        elif isinstance(something, pd.Timestamp):
            date_ret = something.to_pydatetime()
        else:
            date_ret = something
    return date_ret


def pd_timedelta_2_timedelta(value):
    if isinstance(value, pd.Timedelta):
        # print(value, 'parse to timedelta')
        dt_value = timedelta(seconds=value.seconds)
    else:
        dt_value = value
    return dt_value


def date2datetime(dt):
    """
    date 类型转换问 datetime类型
    :param dt:
    :return:
    """
    return datetime(dt.year, dt.month, dt.day)


def clean_datetime_remove_time_data(dt):
    """
    将时间对象的 时、分、秒 全部清零
    :param dt:
    :return:
    """
    return datetime(dt.year, dt.month, dt.day)


def clean_datetime_remove_ms(dt: datetime):
    """
    将时间对象的 毫秒 全部清零
    :param dt:
    :return:
    """
    return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def utc2local(utc):
    localtime = datetime.utcfromtimestamp(utc).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
    return localtime


def is_any(iterable, func):
    """
    查找是否存在任何一个为True的结果，否则返回False
    :param iterable:
    :param func:
    :return:
    """
    for x in iterable:
        if func(x):
            return True
    else:
        return False


def is_not_nan_or_none(x):
    """
    判断是否不是 NAN 或 None
    :param x:
    :return:
    """
    return False if x is None else not ((isinstance(x, float) and np.isnan(x)) or pd.isna(x))


def is_nan_or_none(x):
    """
    判断是否是 NAN 或 None
    :param x:
    :return:
    """
    return True if x is None else (isinstance(x, float) and np.isnan(x)) or pd.isna(x)


def try_2_float(data):
    try:
        return None if data is None else float(data)
    except:
        logger.exception('%s 转化失败', data)
        return None


def str_2_float(sth) -> (float, None):
    """将数据转换成 float 类型，如果是None， NAT， NAN等数据就变成 None"""
    try:
        ret_val = None if is_nan_or_none(sth) else float(sth)
    except TypeError:
        ret_val = sth

    return ret_val


def format_2_str(value, formator):
    """根据 formator 将对象格式化成 str"""
    if formator is None:
        text = str(value)
    elif isinstance(formator, str):
        text = str.format(formator, value)
    elif callable(formator):
        text = formator(value)
    else:
        raise ValueError('%s: %s 无效', value, formator)
    return text


def replace_none_2_str(string, replace=''):
    return replace if string is None else string


def str_2_date(date_str, date_str_format=STR_FORMAT_DATE):
    """
    将日期字符串转换成 date 类型对象，如果字符串为 None 则返回None
    :param date_str: 日期字符串
    :param date_str_format: 日期字符串格式
    :return:
    """
    if date_str is not None:
        if type(date_str) == str:
            date_ret = datetime.strptime(date_str, date_str_format).date()
        elif type(date_str) in (pd.Timestamp, datetime):
            date_ret = date_str.date()
        else:
            date_ret = date_str
    else:
        date_ret = date_str
    return date_ret


def is_pattern_type(obj):
    """
    判断当前对象是否是 Pattern 类
    3.7以后 re._pattern_type 被废弃，re.Pattern开始启用。此写法为了兼容3.6. 以及 3.7 以后版本
    :param obj:
    :return:
    """
    try:
        return isinstance(obj, re.Pattern)
    except AttributeError:
        return isinstance(obj, re._pattern_type)


def counting_years(date_from_str, date_to_str):
    """
    用于计算两个日期之间相差多少年？返回float类型
    :param date_from_str:
    :param date_to_str:
    :return:
    """
    # date_from_str, date_to_str = '2018-05-01', '2019-05-31'
    date_from = str_2_date(date_from_str)
    date_to = str_2_date(date_to_str)

    year_start = str_2_date(f'{date_from.year}-01-01')
    year_end = str_2_date(f'{date_from.year}-12-31')
    ret_val1 = ((year_end - date_from).days + 1) / ((year_end - year_start).days + 1)

    year_start = str_2_date(f'{date_to.year}-01-01')
    year_end = str_2_date(f'{date_to.year}-12-31')
    ret_val2 = ((date_to - year_start).days + 1) / ((year_end - year_start).days + 1)

    ret_val = ret_val1 + ret_val2 + (date_to.year - date_from.year - 1)

    return ret_val


def get_cntr_kind_name(contract_name):
    left_idx = len(contract_name) - 1
    for num_str in '1234567890':
        idx = contract_name.find(num_str, 0, left_idx)
        if idx == -1:
            continue
        if idx < left_idx:
            left_idx = idx
        if left_idx <= 1:
            break
    # print(lidx, contractname[:lidx])
    return contract_name[:left_idx]


if __name__ == "__main__":
    pass
