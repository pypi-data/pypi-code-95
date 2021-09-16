# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import pprint
pp = pprint.PrettyPrinter(indent=2)



CommonFormat = "%(asctime)s | %(levelname)s | [%(process)s/%(processName)s][%(thread)s/%(threadName)s]"
MainFormat = f'{CommonFormat} | %(module)s.%(funcName)s[%(lineno)s] | %(message)s'
DecoFormat = f'{CommonFormat} | %(message)s'
# logging.basicConfig(format=MainFormat, level=logging.DEBUG)
LogLevel = logging.DEBUG
print('LogLevel:', LogLevel, type(LogLevel), 'at', __file__)



logger = logging.getLogger('Basic')
logger.setLevel(LogLevel)
sh = logging.StreamHandler()
sh.setLevel(LogLevel)
formatter = logging.Formatter(MainFormat)
sh.setFormatter(formatter)
logger.addHandler(sh)


decologger = logging.getLogger('Decorator')
decologger.setLevel(LogLevel)
_sh = logging.StreamHandler()
_sh.setLevel(LogLevel)
_formatter = logging.Formatter(DecoFormat)
_sh.setFormatter(_formatter)
decologger.addHandler(_sh)



def funcIdentity(f):
    def __funcIdentity(*args, **kwargs):
        loc = f"{f.__module__}.{f.__qualname__}"
        if len(args) > 1: loc = f"{loc} | {list(args)[1:]}"
        if len(kwargs) > 1: loc = f"{loc} | {kwargs}"
        decologger.debug(msg=loc)
        return f(*args, **kwargs)
    return __funcIdentity


class DebugTools(object):

    def __init__(self):
        self.gubun_len = 100

    def ModuleGubun(self, _file_):
        print(f"{'@'*self.gubun_len} {_file_}")

    def PartGubun(self, s):
        print(f"\n\n{'='*self.gubun_len} {s}")

    def SectionGubun(self, s):
        print(f"\n{'-'*self.gubun_len} {s}")

    def loop(self, loc, i, _len, msg=None):
        _msg = f"{loc} {'-'*50} {i}/{_len}"
        msg = _msg if msg is None else f"{_msg} | {msg}"
        logger.debug(msg)

    def pretty_title(self, s, simbol='*', width=100):
        space = " " * int((width - len(s)) / 2)
        line = simbol * width
        print(f"{line}\n{space}{s}{space}\n{line}")

    def dict(self, obj, loc=None):
        loc = '-'*50 if loc is None else loc
        logger.debug(f"{loc} | {obj}.__dict__:")
        self.pretty_title(f"{obj}.__dict__")
        pp.pprint(obj.__dict__)

    def dir(self, obj):
        self.pretty_title(f"dir({obj})")
        pp.pprint(dir(obj))

    def dictValue(self, loc, msg, dic):
        logger.debug(f"{loc} | {msg}")
        pp.pprint(dic)

    def attrs(self, cls):
        for a in dir(cls):
            print(f"{'-'*self.gubun_len} {a}")
            v = getattr(cls, a)
            print(type(v))
            print(callable(v))
            if callable(v):
                try:
                    rv = v()
                except Exception as e:
                    print(f"Error: {e}")
                else:
                    print('rv:', rv)


dbg = DebugTools()

GUBUNLEN = 100
def moduleGubun(_file_):
    print(f"{'@'*GUBUNLEN} {_file_}")


def PartGubun(partnm):
    print(f"\n\n{'='*GUBUNLEN} {partnm}")


def SectionGubun(sectnm):
    print(f"\n{'-'*GUBUNLEN} {sectnm}")


def _convert_timeunit(seconds):
    sec = 1
    msec = sec / 1000
    min = sec * 60
    hour = min * 60

    t = seconds
    if t < sec:
        unit = 'msec'
        t = t / msec
    elif sec <= t <= min:
        unit = 'secs'
    elif min < t <= hour:
        unit = 'mins'
        t = t / min
    else:
        unit = 'hrs'
        t = t / hour

    return round(t, 1), unit


def utestfunc(f):
    def _utestfunc(*args, **kwargs):
        start_dt = datetime.now()

        loc = f"{f.__module__}.{f.__qualname__}"
        if len(args) > 1: loc = f"{loc} | {list(args)[1:]}"
        if len(kwargs) > 1: loc = f"{loc} | {kwargs}"
        decologger.debug(msg=loc)

        rv = f(*args, **kwargs)

        timeExp, unit = _convert_timeunit(
                        (datetime.now() - start_dt).total_seconds())

        decologger.debug(msg=f"{loc} | Runtime: {timeExp} ({unit})")

        return rv
    return _utestfunc


def loop(loc, i, _len, msg=None):
    _msg = f"{loc} {'-'*50} {i}/{_len}"
    msg = _msg if msg is None else f"{_msg} | {msg}"
    logger.debug(msg)


def view_dict(obj, loc=None):
    try:

        loc = '-'*50 if loc is None else loc
        logger.debug(f"{loc} | {obj}.__dict__:")
        pp.pprint(obj.__dict__)
    except Exception as e:
        logger.exception(e)


def view_dir(obj):
    try:
        print(f"\n\n{'-'*50} dir({obj}):")
        pp.pprint(dir(obj))
    except Exception as e:
        logger.exception(e)


def dictValue(loc, msg, dic):
    logger.debug(f"{loc} | {msg}")
    pp.pprint(dic)


def pretty_title(s, simbol='*', width=100):
    space = " " * int((width - len(s)) / 2)
    line = simbol * width
    print(f"{line}\n{space}{s}{space}\n{line}")
