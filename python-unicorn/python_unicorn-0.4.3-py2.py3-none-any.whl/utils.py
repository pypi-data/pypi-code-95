# -*- coding: utf-8 -*-

import pickle
import codecs
import xlrd
import numpy as np
import sys
from collections import namedtuple

DATA_X_COL_IDX = 7
DATA_Y_COL_IDX = 8
UniFunc = namedtuple('UniFunc',
    'name ename from_field to_field description args code code_str data_x data_y')


def pickle_obj(obj, coding='base64'):
    """Pickle object into string for being a REST parameter.
    """
    return codecs.encode(pickle.dumps(obj), coding).decode()


class UnicornData(object):
    """Parsing data from external xlsx file.

    Examples
    --------
    >>> f = 'data.xlsx'
    >>> data = UnicornData(f)
    >>> for f in data.functions:
    >>>     client.create(**f)
    >>> # client is an AdminClient instance
    >>>
    """
    def __init__(self, xlsx_file, **kws):
        try:
            book = xlrd.open_workbook(xlsx_file)
        except:
            print("Open xlsx file failed.")
            sys.exit(1)
        self.data_x_col_idx = kws.get('data_x_col_idx', DATA_X_COL_IDX)
        self.data_y_col_idx = kws.get('data_y_col_idx', DATA_Y_COL_IDX)
        self.sheet = book.sheet_by_index(0)
        self.ncols, self.nrows = self.sheet.ncols, self.sheet.nrows
        self.header = [x.value for x in self.sheet.row(0)]
        self.functions = self.generate_functions()

    def generate_functions(self):
        for ridx in range(1, self.nrows):
            row = [v.value for v in self.sheet.row(ridx)]

            x_raw = row[self.data_x_col_idx]
            row[self.data_x_col_idx] = pickle_obj(
                    np.array([float(v) for v in x_raw.split()]))

            y_raw = row[self.data_y_col_idx]
            row[self.data_y_col_idx] = pickle_obj(
                    np.array([float(v) for v in y_raw.split()]))
            f = dict(zip(self.header, row))
            yield to_tuple(f)


def to_tuple(f):
    """Convert dict *f* to namedTuple.
    """
    attr = {k: v for k, v in f.items()}
    attr['code_str'] = attr['code']
    attr['code'] = get_func(attr['code'])
    return UniFunc(**attr)


def get_func(fstr):
    """Return function object from code.
    """
    fncode, ns = compile(fstr, "<string>", "exec"), {}
    exec(fncode, ns)
    return ns.get('f')


def to_dict(d):
    ret = {}
    for k,v in d.items():
        try:
            ret[k] = float(v)
        except:
            ret[k] = v
    return ret
