'''pipe file to connect core files and application files'''
import sys
from contextlib import contextmanager
from pathlib import Path

import codefast as cf
from .authorization import Authorization


sys.path.insert(0, str(Path.home()) + '/.config')


@contextmanager
def _init_author():
    try:
        from cccache import FERNET_KEY, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
        yield Authorization(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, FERNET_KEY)
    except Exception as e:
        cf.warning(str(e))
        yield None

with _init_author() as _author:
    author = _author
