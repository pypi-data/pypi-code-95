# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2018-03-07 23:33:18
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-03-08 16:06:42
from __future__ import absolute_import
import warnings
import traceback
from scrapy.utils.misc import walk_modules
from scrapy.spiderloader import SpiderLoader
import sys

class easySpiderLoader(SpiderLoader):
    def _load_all_spiders(self):
        for name in self.spider_modules:
            try:
                for module in walk_modules(name):
                    # print module
                    if sys.version_info > (3, ):
                        from importlib import reload
                    else:
                        from imp import reload
                    reload(module)
                    self._load_spiders(module)
            except ImportError:
                if self.warn_only:
                    msg = ("\n{tb}Could not load spiders from module '{modname}'. "
                           "See above traceback for details.".format(
                               modname=name, tb=traceback.format_exc()))
                    warnings.warn(msg, RuntimeWarning)
                else:
                    raise
        try:
            # 1.4 之前的版本，不存在这个函数
            self._check_name_duplicates()
        except AttributeError:
            pass
