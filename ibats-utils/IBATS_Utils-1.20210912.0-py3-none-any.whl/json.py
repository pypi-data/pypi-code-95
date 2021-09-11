#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/6/20 下午12:23
@File    : json.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import json
import logging
import typing
from datetime import datetime, date
from enum import Enum

import numpy as np
import simplejson

from ibats_utils.transfer import datetime_2_str, date_2_str

logger = logging.getLogger(__name__)


class JsonEncoder(json.JSONEncoder):
    """Json编码器"""

    def default(self, obj):
        if isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        elif isinstance(obj, np.float64) or isinstance(obj, np.float32) or isinstance(obj, np.float16):
            return float(obj)
        elif isinstance(obj, datetime):
            return datetime_2_str(obj)
        elif isinstance(obj, date):
            return date_2_str(obj)
        elif isinstance(obj, Enum):
            return obj.name


class SimpleJsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        elif isinstance(obj, np.float64) or isinstance(obj, np.float32) or isinstance(obj, np.float16):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, datetime):
            return datetime_2_str(obj)
        elif isinstance(obj, date):
            return date_2_str(obj)
        elif isinstance(obj, Enum):
            return obj.name


def dict_2_jsonable(dic: typing.Dict, **kwargs) -> typing.Dict:
    """将字典对象中的各项转换为可Json的对象"""
    kwargs.setdefault('ignore_nan', True)
    kwargs.setdefault('cls', SimpleJsonEncoder)
    return json.loads(obj_2_json(dic, **kwargs))


def obj_2_json(dic: typing.Union[typing.Dict, typing.List], **kwargs) -> str:
    """将字典/列表对象转换为Json字符串"""
    kwargs.setdefault('ignore_nan', True)
    kwargs.setdefault('cls', SimpleJsonEncoder)
    return simplejson.dumps(dic, **kwargs)


def _test_dict_2_jsonable():
    class EnumTest(Enum):
        T1 = 't1'
        T2 = 't2'

    obj = dict(
        dt=datetime.now(),
        date=date.today(),
        float64=np.float64(2.34),
        nan=np.nan,
        enum=EnumTest.T2
    )
    ret = dict_2_jsonable(obj)
    print(ret)
    expect = {'dt': datetime_2_str(obj['dt']), 'date': date_2_str(obj['date']), 'float64': 2.34, 'nan': None,
              'enum': 'T2'}
    assert all([k1 == k2 and v1 == v2 for (k1, v1), (k2, v2) in zip(ret.items(), expect.items())])


if __name__ == "__main__":
    _test_dict_2_jsonable()
