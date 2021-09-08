# Author     : lin le
# CreateTime : 2021/8/31 16:20
# Email      : linle861021@163.com

import sys

__version__ = '1.0.7'
if sys.version < '3.6':
    raise RuntimeError('python version required 3.6+')

from .simpleprocessbar import SimpleProcessbar
