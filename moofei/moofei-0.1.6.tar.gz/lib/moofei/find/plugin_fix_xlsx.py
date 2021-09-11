#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

import warnings
import six
try:
    import xlrd
except ImportError:
    warnings.warn('Please Import xlrd TO pip')
    xlrd = None
    
try:
    from .cplugin_fix import _StringIO, StringIO, cPlugin_Fix
except (ImportError,ValueError):
    from cplugin_fix import _StringIO, StringIO, cPlugin_Fix   
from moofei._find import _strtypes,_find_func,_search_func

class Plugin_Fix_Xlsx(cPlugin_Fix):
    def is_enable(self):
        return xlrd
        
    def child_read(self, sheet_name):
        return self.__class___(self.fpath,self.words,self.wcase, self.fp, **self.__awgs)

    def all_texts(self):
        fpath = self.get_tempfile_or_path(suffix=True)
        workbook = xlrd.open_workbook(fpath)

        sheet_names = workbook.sheet_names()
        Ls = []
        for name in sheet_names:
            worksheet = workbook.sheet_by_name(name)
            num_rows = worksheet.nrows
            num_cells = worksheet.ncols

            for row in range(num_rows):
                rows = worksheet.row(row)
                #print(rows)
                lines = []
                for col in range(num_cells):
                    s = worksheet.cell_value(row, col)
                    if s:
                        if isinstance(s, (int, float)):
                            s = six.text_type(s)
                        lines.append(s)
                if lines:
                    Ls.append(u' '.join(lines))
        return u'\n'.join(Ls)
        
    
        
