import json
import os
import stat
from typing import Dict, List

import treefiles as tf


def dump_data(fname, data: Dict[str, List[str]]):
    opts = dict(separators=(",", ":"))
    enc_dir = lambda x: f"'{json.dumps(x, **opts)}'"

    _data, n_rows = [], len(next(iter(data.values())))
    for i in range(n_rows):
        row = {}
        for k in data:
            row[k] = data[k][i]
        _data.append(row)

    data1 = [[enc_dir(d)] for d in _data]
    tf.dump_txt(fname, data1)


def dump(fname, content):
    with open(fname, "w") as f:
        f.write(content)


def dump_exe(fname, content):
    dump(fname, content)
    os.chmod(fname, os.stat(fname).st_mode | stat.S_IEXEC)
