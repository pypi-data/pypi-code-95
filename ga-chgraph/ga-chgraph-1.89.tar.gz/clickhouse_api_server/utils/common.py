import time
import numpy as np


def success_request(data, response):
    res = {}
    res["data"] = data if data else {}
    res["context"] = response if response else {"code": 200, "timestamp": time.time()}
    return res


def fail_request(data, response, e):
    res = {}
    res["data"] = data if data else {}

    if response:
        res["context"] = response
    else:
        message = str(e) if e else "系统异常"
        res["context"] = {"code": 500, "timestamp": time.time(), "massage": message}

    return res


def tostr(obj):
    if type(obj) == list:
        return str(obj)
    elif type(obj) == np.ndarray:
        return np.array2string(obj, separator=',', threshold=1000000000, max_line_width=1000000000)

