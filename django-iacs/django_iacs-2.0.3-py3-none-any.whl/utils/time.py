# coding:utf-8
import time
from datetime import datetime

import pytz
from django.utils import timezone


def get_current_time_by_microsecond():
    """
    将当前时间计算成微秒
    :return: 微妙
    """
    return int(timezone.now().timestamp() * 1000000)


def to_local_time(d):
    if isinstance(d, datetime):
        return d.replace(tzinfo=timezone.utc)
    else:
        raise TypeError


def time_to_string(d):
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d %H:%M:%S")
    else:
        raise TypeError


def us_timestamp_to_str(timestamp):
    if isinstance(timestamp, int) or isinstance(timestamp, float):
        data_array = datetime.utcfromtimestamp(timestamp / 1000000)
        return data_array.strftime("%Y-%m-%d %H:%M:%S")
    else:
        raise TypeError


def string_to_time(s):
    if isinstance(s, str):
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    else:
        raise TypeError


def time_to_timestamp(d):
    if isinstance(d, str):
        return string_to_time(d).timestamp()
    elif isinstance(d, datetime):
        return d.timestamp()
    else:
        raise TypeError


def utc_to_timestamp(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%SZ'):
    """
    utc转换为微妙时间戳
    :param utc_time_str:
    :param utc_format: 时间格式
    :return:
    """
    local_tz = pytz.timezone('Asia/Shanghai')
    local_format = "%Y-%m-%d %H:%M"
    utc_dt = datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)
    return int(time.mktime(time.strptime(time_str, local_format))) * 1000


def utc_to_string(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%SZ'):
    local_tz = pytz.timezone('Asia/Shanghai')
    local_format = "%Y-%m-%d %H:%M"
    utc_dt = datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)
    return us_timestamp_to_str(int(time.mktime(time.strptime(time_str, local_format))) * 1000000)
