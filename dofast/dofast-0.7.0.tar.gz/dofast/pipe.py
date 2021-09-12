'''pipe file to connect core files and application files'''
import sys
from contextlib import contextmanager
from pathlib import Path

import codefast as cf

from .authorization import Authorization


@contextmanager
def alter_syspath():
    _config_file = str(Path.home()) + "/.config/cccache.py"
    if cf.io.exists(_config_file):
        sys.path.insert(0, str(Path.home()) + '/.config')
        yield True
    else:
        yield False


def _init_author():
    with alter_syspath() as exec_result:
        if exec_result:
            from cccache import (FERNET_KEY, REDIS_HOST, REDIS_PASSWORD,
                                 REDIS_PORT)
            yield Authorization(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD,
                                 FERNET_KEY)
        else:
            yield None


author = next(_init_author())


