
"""
Main/General category
"""

import importlib
import random
import string
import sys


class ObjDebug(object):

    """
    Apply this to a class and you will be able to edit the methods of that class and have it update in real time.

    Source: https://stackoverflow.com/a/15839513/12590728
    """

    def __getattribute__(self, k):
        ga = object.__getattribute__
        sa = object.__setattr__
        cls = ga(self, "__class__")
        modname = cls.__module__
        mod = __import__(modname)
        del sys.modules[modname]
        importlib.reload(mod)
        sa(self, "__class__", getattr(mod, cls.__name__))
        return ga(self, k)


class DatetimeTools:

    """
    Just a fast way of formatting dates with .strftime
    """

    def formatShort(dt):
        return dt.strftime("%b %d %Y at %I:%M %p")

    def formatLong(dt):
        return dt.strftime("%B %d %Y at %I:%M %p")


def convertRange(val: float, old: tuple, new: tuple):
    """
    Converts the range of a value to a new range.

    Example
    -------
    convertRange(50, (0, 100), (0, 1))
    >> 0.5
    """

    return (((val - old[0]) * (new[1] - new[0])) / (old[1] - old[0])) + new[0]


def timeRound(t: int, r: int = 3):
    """
    Well, it's so self explanatory. (There's a reason why I did this)
    """

    return round(t, r)


def generateId(n: int, dictionary: str = None):
    """
    Generate an Id

    Parameters
    ----------
    `n` : int
        How long the id is. (Length of characters)
    `dictionary` : str
        Where to look for characters.
    """

    if not dictionary:
        dictionary = string.ascii_letters + string.digits

    return "".join(random.choices(dictionary, k=n))
